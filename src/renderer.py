import os

import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import config


class Renderer:
    def __init__(self):
        self.language = config.LANGUAGE
        self.landmark_style = config.LANDMARK_STYLE
        self.color_mode = config.COLOR_MODE
        self.display_size = (config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)
        self._font_path = self._find_font_path()
        self._drawer = mp.solutions.drawing_utils
        self._styles = mp.solutions.drawing_styles
        self._hands = mp.solutions.hands

    def cycle_landmark_style(self):
        styles = config.LANDMARK_STYLES
        current_index = styles.index(self.landmark_style) if self.landmark_style in styles else 0
        self.landmark_style = styles[(current_index + 1) % len(styles)]
        print(f"关键点显示已切换为：{self.landmark_style}")
        return self.landmark_style

    def cycle_language(self):
        languages = config.LANGUAGES
        current_index = languages.index(self.language) if self.language in languages else 0
        self.language = languages[(current_index + 1) % len(languages)]
        print(f"界面语言已切换为：{self.language}")
        return self.language

    def cycle_color_mode(self):
        modes = config.COLOR_MODES
        current_index = modes.index(self.color_mode) if self.color_mode in modes else 0
        self.color_mode = modes[(current_index + 1) % len(modes)]
        print(f"画面色彩已切换为：{self.color_mode}")
        return self.color_mode

    def set_display_size(self, width, height):
        if width > 0 and height > 0:
            self.display_size = (width, height)

    def _find_font_path(self):
        for path in config.FONT_PATHS:
            if os.path.exists(path):
                return path
        return None

    def _draw_text(self, frame, text, position, font_size, color, stroke_width=0, stroke_fill=(0, 0, 0)):
        if self._font_path is None:
            cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_size / 28, color, max(1, stroke_width + 1), cv2.LINE_AA)
            return

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(self._font_path, font_size)
        rgb_color = (color[2], color[1], color[0])
        rgb_stroke = (stroke_fill[2], stroke_fill[1], stroke_fill[0])
        draw.text(position, text, font=font, fill=rgb_color, stroke_width=stroke_width, stroke_fill=rgb_stroke)
        frame[:] = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    def _gesture_label(self, gesture):
        labels = {
            "zh": {"pinch": "捏合", "index": "食指", "both": "混合"},
            "en": {"pinch": "Pinch", "index": "Index", "both": "Both"},
        }
        return labels.get(self.language, labels["zh"]).get(gesture, gesture)

    def _tool_name(self, item):
        return item["zh_name"] if self.language == "zh" else item["name"]

    def prepare_display_frame(self, frame, fullscreen_enabled):
        if not fullscreen_enabled:
            return frame
        target_size = self.display_size
        if config.FULLSCREEN_SCALE_MODE == "cover":
            return self._resize_cover(frame, target_size)
        return cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)

    def build_base_frame(self, frame, framing_rect=None):
        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        grayscale_frame = cv2.cvtColor(grayscale, cv2.COLOR_GRAY2BGR)
        output = grayscale_frame if self.color_mode == "grayscale" else frame.copy()
        if framing_rect is not None:
            dimmed = output.copy()
            overlay = output.copy()
            overlay[:] = (0, 0, 0)
            dimmed = cv2.addWeighted(dimmed, 0.78, overlay, 0.22, 0)
            x1, y1, x2, y2 = framing_rect
            framed_region = frame if self.color_mode == "grayscale" else grayscale_frame
            dimmed[y1:y2, x1:x2] = framed_region[y1:y2, x1:x2]
            self._draw_viewfinder(dimmed, framing_rect)
            return dimmed
        return output

    def draw_palette(self, frame, paint_layer):
        rects = []
        x = config.PALETTE_MARGIN
        y = config.PALETTE_MARGIN
        panel_padding = 10
        panel_width = len(config.PALETTE) * config.PALETTE_BOX_WIDTH + (len(config.PALETTE) - 1) * config.PALETTE_GAP + panel_padding * 2
        panel_height = config.PALETTE_BOX_HEIGHT + panel_padding * 2
        self._blend_rect(frame, (x - panel_padding, y - panel_padding, x - panel_padding + panel_width, y - panel_padding + panel_height), config.UI_PANEL_COLOR, config.UI_PANEL_ALPHA)

        for index, item in enumerate(config.PALETTE):
            x2 = x + config.PALETTE_BOX_WIDTH
            y2 = y + config.PALETTE_BOX_HEIGHT
            rects.append((x, y, x2, y2))
            fill_color = (42, 45, 52) if item["eraser"] else item["color"]
            cv2.rectangle(frame, (x, y), (x2, y2), fill_color, -1)

            if paint_layer.hover_progress(index) > 0:
                progress_width = int(config.PALETTE_BOX_WIDTH * paint_layer.hover_progress(index))
                cv2.rectangle(frame, (x, y2 - 4), (x + progress_width, y2), config.UI_ACCENT_COLOR, -1)

            border_color = config.UI_ACCENT_COLOR if index == paint_layer.current_palette_index else (95, 105, 118)
            border_thickness = 3 if index == paint_layer.current_palette_index else 1
            cv2.rectangle(frame, (x, y), (x2, y2), border_color, border_thickness)
            label = item["key"] if not item["eraser"] else "E"
            cv2.putText(frame, label, (x + 20, y + 26), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
            x = x2 + config.PALETTE_GAP
        return rects

    def draw_status(self, frame, gesture_state, paint_layer, brush_gesture_mode):
        height, width = frame.shape[:2]
        y1 = height - config.UI_STATUS_HEIGHT - config.UI_MARGIN
        y2 = height - config.UI_MARGIN
        x1 = config.UI_MARGIN
        x2 = width - config.UI_MARGIN
        self._blend_rect(frame, (x1, y1, x2, y2), config.UI_PANEL_COLOR, config.UI_PANEL_ALPHA)

        if self.language == "zh":
            mode = "框选" if gesture_state.framing_active else "绘画" if gesture_state.painting_active else "待机"
            hint = "按键：1-6 颜色 | G 手势 | T 语言 | L 关键点 | V 画面 | F 全屏 | C 清空 | Q 退出"
            gesture_prefix = "手势"
            tool_prefix = "工具"
            view_prefix = "画面"
            view_mode = "黑白" if self.color_mode == "grayscale" else "彩色"
        else:
            mode = "FRAME" if gesture_state.framing_active else "PAINT" if gesture_state.painting_active else "IDLE"
            hint = "Keys: 1-6 Color | G Gesture | T Language | L Landmarks | V View | F Fullscreen | C Clear | Q Quit"
            gesture_prefix = "Gesture"
            tool_prefix = "Tool"
            view_prefix = "View"
            view_mode = "Gray" if self.color_mode == "grayscale" else "Color"

        mode_color = config.UI_FRAME_COLOR if gesture_state.framing_active else config.UI_SUCCESS_COLOR if gesture_state.painting_active else config.UI_MUTED_TEXT_COLOR
        self._draw_badge(frame, (x1 + 16, y1 + 18), mode, mode_color)

        gesture = self._gesture_label(gesture_state.brush_gesture or brush_gesture_mode)
        color_name = self._tool_name(paint_layer.current_item)
        text = f"{gesture_prefix}: {gesture}   {tool_prefix}: {color_name}   {view_prefix}: {view_mode}   {hint}"
        self._draw_text(frame, text, (x1 + 115, y1 + 30), 18, config.UI_TEXT_COLOR)

    def draw_brush_cursor(self, frame, brush_point, paint_layer):
        if brush_point is None:
            return
        if paint_layer.current_item["eraser"]:
            radius = max(config.ERASER_THICKNESS // 2, 12)
            cv2.circle(frame, brush_point, radius, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.line(frame, (brush_point[0] - radius, brush_point[1]), (brush_point[0] + radius, brush_point[1]), (255, 255, 255), 1, cv2.LINE_AA)
            cv2.line(frame, (brush_point[0], brush_point[1] - radius), (brush_point[0], brush_point[1] + radius), (255, 255, 255), 1, cv2.LINE_AA)
            return

        color = paint_layer.current_item["color"]
        radius = max(config.BRUSH_THICKNESS + 4, 12)
        cv2.circle(frame, brush_point, radius + 3, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.circle(frame, brush_point, radius, color, 2, cv2.LINE_AA)
        cv2.circle(frame, brush_point, 3, color, -1, cv2.LINE_AA)

    def draw_landmarks(self, frame, hands, gesture_state=None):
        if self.landmark_style == "off":
            return
        if self.landmark_style == "full":
            for hand in hands:
                proto = self._build_landmark_proto(hand["landmarks"], frame.shape[1], frame.shape[0])
                self._drawer.draw_landmarks(
                    frame,
                    proto,
                    self._hands.HAND_CONNECTIONS,
                    self._styles.get_default_hand_landmarks_style(),
                    self._styles.get_default_hand_connections_style(),
                )
            return

        for hand in hands:
            landmarks = hand["landmarks"]
            for start, end in self._hands.HAND_CONNECTIONS:
                cv2.line(frame, landmarks[start], landmarks[end], (90, 120, 150), 1, cv2.LINE_AA)
            for index in (4, 8, 12, 16, 20):
                cv2.circle(frame, landmarks[index], 3, (180, 200, 220), -1, cv2.LINE_AA)
        if gesture_state and gesture_state.brush_point:
            cv2.circle(frame, gesture_state.brush_point, 6, config.UI_ACCENT_COLOR, -1, cv2.LINE_AA)

    def _draw_viewfinder(self, frame, rect):
        x1, y1, x2, y2 = rect
        color = config.UI_FRAME_COLOR
        length = max(24, min(x2 - x1, y2 - y1) // 5)
        thickness = 4
        corners = [
            ((x1, y1), (x1 + length, y1), (x1, y1 + length)),
            ((x2, y1), (x2 - length, y1), (x2, y1 + length)),
            ((x1, y2), (x1 + length, y2), (x1, y2 - length)),
            ((x2, y2), (x2 - length, y2), (x2, y2 - length)),
        ]
        for origin, horizontal, vertical in corners:
            cv2.line(frame, origin, horizontal, color, thickness, cv2.LINE_AA)
            cv2.line(frame, origin, vertical, color, thickness, cv2.LINE_AA)
        label = "框选区域" if self.language == "zh" else "FRAME SELECT"
        self._draw_text(frame, label, (x1, max(0, y1 - 30)), 20, color, 1)

    def _draw_badge(self, frame, origin, text, color):
        x, y = origin
        text_size, _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.58, 2)
        width = text_size[0] + 22
        height = 30
        cv2.rectangle(frame, (x, y), (x + width, y + height), color, -1)
        self._draw_text(frame, text, (x + 11, y + 5), 18, (20, 24, 30))

    def _blend_rect(self, frame, rect, color, alpha):
        x1, y1, x2, y2 = rect
        x1 = max(0, min(frame.shape[1], x1))
        x2 = max(0, min(frame.shape[1], x2))
        y1 = max(0, min(frame.shape[0], y1))
        y2 = max(0, min(frame.shape[0], y2))
        if x2 <= x1 or y2 <= y1:
            return
        overlay = frame[y1:y2, x1:x2].copy()
        overlay[:] = color
        frame[y1:y2, x1:x2] = cv2.addWeighted(overlay, alpha, frame[y1:y2, x1:x2], 1 - alpha, 0)

    def _resize_cover(self, frame, target_size):
        target_width, target_height = target_size
        height, width = frame.shape[:2]
        scale = max(target_width / width, target_height / height)
        resized_width = int(width * scale)
        resized_height = int(height * scale)
        resized = cv2.resize(frame, (resized_width, resized_height), interpolation=cv2.INTER_LINEAR)
        x1 = max(0, (resized_width - target_width) // 2)
        y1 = max(0, (resized_height - target_height) // 2)
        return resized[y1:y1 + target_height, x1:x1 + target_width]

    def _build_landmark_proto(self, landmarks, frame_width, frame_height):
        from mediapipe.framework.formats import landmark_pb2

        proto = landmark_pb2.NormalizedLandmarkList()
        for x, y in landmarks:
            proto.landmark.add(x=x / frame_width, y=y / frame_height, z=0.0)
        return proto
