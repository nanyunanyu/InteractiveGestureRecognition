from dataclasses import dataclass

import config
from utils import angle_degrees, clamp_rect, distance, midpoint, smooth_point, smooth_rect


@dataclass
class GestureState:
    framing_active: bool = False
    framing_rect: tuple | None = None
    painting_active: bool = False
    brush_point: tuple | None = None
    brush_gesture: str | None = None
    pinch_ratio: float | None = None


class GestureEngine:
    def __init__(self):
        self.brush_gesture_mode = config.BRUSH_GESTURE_MODE
        self._framing_enter_count = 0
        self._framing_exit_count = 0
        self._brush_enter_count = 0
        self._brush_exit_count = 0
        self._smoothed_rect = None
        self._smoothed_brush_point = None
        self._framing_latched = False
        self._brush_latched = False
        self._active_brush_gesture = None

    def cycle_brush_gesture_mode(self):
        modes = config.BRUSH_GESTURE_MODES
        current_index = modes.index(self.brush_gesture_mode) if self.brush_gesture_mode in modes else 0
        self.brush_gesture_mode = modes[(current_index + 1) % len(modes)]
        self._brush_enter_count = 0
        self._brush_exit_count = 0
        self._brush_latched = False
        self._active_brush_gesture = None
        self._smoothed_brush_point = None
        return self.brush_gesture_mode

    def update(self, hands, frame_shape):
        state = GestureState()

        framing_rect = self._detect_framing_rect(hands, frame_shape)
        if framing_rect is not None:
            self._framing_enter_count += 1
            self._framing_exit_count = 0
            self._smoothed_rect = smooth_rect(self._smoothed_rect, framing_rect, config.RECT_SMOOTHING)
            if self._framing_enter_count >= config.FRAMING_ENTER_FRAMES:
                self._framing_latched = True
        else:
            self._framing_enter_count = 0
            if self._framing_latched:
                self._framing_exit_count += 1
                if self._framing_exit_count >= config.FRAMING_EXIT_FRAMES:
                    self._framing_latched = False
                    self._smoothed_rect = None
            else:
                self._framing_exit_count = 0

        if self._framing_latched and self._smoothed_rect is not None:
            state.framing_active = True
            state.framing_rect = self._smoothed_rect
            self._brush_enter_count = 0
            self._brush_exit_count = 0
            self._brush_latched = False
            self._active_brush_gesture = None
            self._smoothed_brush_point = None
            return state

        brush_result = self._detect_brush(hands)
        if brush_result is not None:
            brush_gesture, brush_point, pinch_ratio = brush_result
            state.pinch_ratio = pinch_ratio
            self._brush_enter_count += 1
            self._brush_exit_count = 0
            self._active_brush_gesture = brush_gesture
            self._smoothed_brush_point = smooth_point(self._smoothed_brush_point, brush_point, config.POINT_SMOOTHING)
            if self._brush_enter_count >= self._enter_frames_for(brush_gesture):
                self._brush_latched = True
        else:
            self._brush_enter_count = 0
            if self._brush_latched:
                self._brush_exit_count += 1
                if self._brush_exit_count >= self._exit_frames_for(self._active_brush_gesture):
                    self._brush_latched = False
                    self._active_brush_gesture = None
                    self._smoothed_brush_point = None
            else:
                self._brush_exit_count = 0
                self._active_brush_gesture = None

        if self._brush_latched and self._smoothed_brush_point is not None:
            state.painting_active = True
            state.brush_point = self._smoothed_brush_point
            state.brush_gesture = self._active_brush_gesture

        return state

    def _detect_brush(self, hands):
        if self.brush_gesture_mode == "pinch":
            return self._detect_pinch(hands, self._brush_latched)
        if self.brush_gesture_mode == "index":
            return self._detect_index(hands)

        pinch_result = self._detect_pinch(hands, self._brush_latched)
        if pinch_result is not None:
            return pinch_result
        return self._detect_index(hands)

    def _enter_frames_for(self, brush_gesture):
        return config.INDEX_ENTER_FRAMES if brush_gesture == "index" else config.PINCH_ENTER_FRAMES

    def _exit_frames_for(self, brush_gesture):
        return config.INDEX_EXIT_FRAMES if brush_gesture == "index" else config.PINCH_EXIT_FRAMES

    def _detect_framing_rect(self, hands, frame_shape):
        if len(hands) < 2:
            return None

        candidate_hands = hands[:2]
        points = []
        spread_ratios = []

        for hand in candidate_hands:
            landmarks = hand["landmarks"]
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            palm_width = max(distance(landmarks[5], landmarks[17]), 1)
            spread_ratio = distance(thumb_tip, index_tip) / palm_width
            spread_ratios.append(spread_ratio)
            points.extend([thumb_tip, index_tip])

        spread_threshold = config.FRAMING_KEEP_SPREAD_RATIO if self._framing_latched else config.FRAMING_MIN_SPREAD_RATIO
        if min(spread_ratios) < spread_threshold:
            return None

        x_values = [point[0] for point in points]
        y_values = [point[1] for point in points]
        x1, x2 = min(x_values), max(x_values)
        y1, y2 = min(y_values), max(y_values)

        width = x2 - x1
        height = y2 - y1
        if width < config.FRAMING_MIN_WIDTH or height < config.FRAMING_MIN_HEIGHT:
            return None

        aspect_ratio = width / max(height, 1)
        if aspect_ratio < config.FRAMING_ASPECT_MIN or aspect_ratio > config.FRAMING_ASPECT_MAX:
            return None

        padding_x = int(width * config.FRAMING_PADDING_RATIO)
        padding_y = int(height * config.FRAMING_PADDING_RATIO)
        rect = (x1 - padding_x, y1 - padding_y, x2 + padding_x, y2 + padding_y)
        return clamp_rect(rect, frame_shape)

    def _detect_pinch(self, hands, latched):
        if not hands:
            return None

        hand = max(hands, key=lambda item: item["score"])
        landmarks = hand["landmarks"]
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        palm_width = max(distance(landmarks[5], landmarks[17]), 1)
        pinch_ratio = distance(thumb_tip, index_tip) / palm_width
        threshold = config.PINCH_END_RATIO if latched else config.PINCH_START_RATIO
        if pinch_ratio > threshold:
            return None
        return "pinch", midpoint(thumb_tip, index_tip), pinch_ratio

    def _detect_index(self, hands):
        if not hands:
            return None

        hand = max(hands, key=lambda item: item["score"])
        landmarks = hand["landmarks"]
        if not self._is_index_extended(landmarks):
            return None
        if self._is_finger_extended(landmarks, 9, 10, 12, config.OTHER_FINGER_FOLDED_RATIO):
            return None
        if self._is_finger_extended(landmarks, 13, 14, 16, config.OTHER_FINGER_FOLDED_RATIO):
            return None
        if self._is_finger_extended(landmarks, 17, 18, 20, config.OTHER_FINGER_FOLDED_RATIO):
            return None
        return "index", landmarks[8], None

    def _is_index_extended(self, landmarks):
        wrist = landmarks[0]
        index_mcp = landmarks[5]
        index_pip = landmarks[6]
        index_tip = landmarks[8]
        extension = distance(wrist, index_tip) / max(distance(wrist, index_pip), 1)
        angle = angle_degrees(index_mcp, index_pip, index_tip)
        return extension >= config.INDEX_EXTEND_RATIO and angle >= config.INDEX_MIN_ANGLE

    def _is_finger_extended(self, landmarks, mcp_index, pip_index, tip_index, ratio):
        wrist = landmarks[0]
        extension = distance(wrist, landmarks[tip_index]) / max(distance(wrist, landmarks[pip_index]), 1)
        angle = angle_degrees(landmarks[mcp_index], landmarks[pip_index], landmarks[tip_index])
        return extension >= ratio and angle >= config.INDEX_MIN_ANGLE
