import cv2
import numpy as np

import config
from utils import point_in_rect


class PaintLayer:
    def __init__(self, frame_width, frame_height):
        self.canvas = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
        self.mask = np.zeros((frame_height, frame_width), dtype=np.uint8)
        self.current_palette_index = 0
        self.last_point = None
        self._hover_counts = [0 for _ in config.PALETTE]

    @property
    def current_item(self):
        return config.PALETTE[self.current_palette_index]

    def update_color_from_point(self, point, palette_rects):
        if point is None:
            self._hover_counts = [0 for _ in config.PALETTE]
            return False

        changed = False
        for index, rect in enumerate(palette_rects):
            if point_in_rect(point, rect):
                self._hover_counts[index] += 1
                if self._hover_counts[index] >= config.PALETTE_HOVER_FRAMES and self.current_palette_index != index:
                    self.current_palette_index = index
                    changed = True
                    self._hover_counts = [0 for _ in config.PALETTE]
                    break
            else:
                self._hover_counts[index] = 0

        return changed

    def stroke(self, point):
        item = self.current_item
        thickness = config.ERASER_THICKNESS if item["eraser"] else config.BRUSH_THICKNESS

        if item["eraser"]:
            if self.last_point is None:
                cv2.circle(self.canvas, point, thickness // 2, (0, 0, 0), -1)
                cv2.circle(self.mask, point, thickness // 2, 0, -1)
            else:
                cv2.line(self.canvas, self.last_point, point, (0, 0, 0), thickness, cv2.LINE_AA)
                cv2.line(self.mask, self.last_point, point, 0, thickness, cv2.LINE_AA)
        else:
            color = item["color"]
            if self.last_point is None:
                cv2.circle(self.canvas, point, thickness // 2, color, -1)
                cv2.circle(self.mask, point, thickness // 2, 255, -1)
            else:
                cv2.line(self.canvas, self.last_point, point, color, thickness, cv2.LINE_AA)
                cv2.line(self.mask, self.last_point, point, 255, thickness, cv2.LINE_AA)

        self.last_point = point

    def end_stroke(self):
        self.last_point = None

    def clear(self):
        self.canvas[:] = 0
        self.mask[:] = 0
        self.last_point = None

    def composite(self, frame):
        output = frame.copy()
        visible = self.mask > 0
        output[visible] = self.canvas[visible]
        return output

    def hover_progress(self, index):
        return min(1.0, self._hover_counts[index] / max(config.PALETTE_HOVER_FRAMES, 1))

    def set_palette_index_from_key(self, key_char):
        for index, item in enumerate(config.PALETTE):
            if item["key"] == key_char:
                self.current_palette_index = index
                self._hover_counts = [0 for _ in config.PALETTE]
                return True
        return False
