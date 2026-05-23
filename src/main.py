import cv2

import config
from gesture_engine import GestureEngine
from hand_tracker import HandTracker
from paint_layer import PaintLayer
from renderer import Renderer
from utils import distance


def _open_camera():
    backends = []
    if hasattr(cv2, "CAP_DSHOW"):
        backends.append((cv2.CAP_DSHOW, "DirectShow"))
    if hasattr(cv2, "CAP_MSMF"):
        backends.append((cv2.CAP_MSMF, "Media Foundation"))
    backends.append((None, "Default"))

    for backend, name in backends:
        capture = cv2.VideoCapture(config.CAMERA_INDEX) if backend is None else cv2.VideoCapture(config.CAMERA_INDEX, backend)
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        for _ in range(10):
            ok, frame = capture.read()
            if ok and frame is not None:
                print(f"摄像头已打开：{name} 后端，索引 {config.CAMERA_INDEX}。")
                return capture, frame
        capture.release()

    raise RuntimeError("无法读取摄像头画面。请检查摄像头权限，或在 src/config.py 中尝试把 CAMERA_INDEX 改成 1。")


def _set_fullscreen(enabled):
    property_value = cv2.WINDOW_FULLSCREEN if enabled else cv2.WINDOW_NORMAL
    cv2.setWindowProperty(config.WINDOW_NAME, cv2.WND_PROP_FULLSCREEN, property_value)


def main():
    capture, frame = _open_camera()

    frame = cv2.flip(frame, 1)
    frame_height, frame_width = frame.shape[:2]

    tracker = HandTracker()
    engine = GestureEngine()
    renderer = Renderer()
    paint_layer = PaintLayer(frame_width, frame_height)
    fullscreen_enabled = config.DEFAULT_FULLSCREEN

    cv2.namedWindow(config.WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(config.WINDOW_NAME, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)
    if hasattr(cv2, "getWindowImageRect"):
        _, _, display_width, display_height = cv2.getWindowImageRect(config.WINDOW_NAME)
        renderer.set_display_size(display_width, display_height)
    _set_fullscreen(fullscreen_enabled)
    print("程序已启动：默认中文界面。1-6 颜色/橡皮，G 切换画笔手势，T 切换语言，L 切换关键点，V 切换画面黑白/彩色，F 全屏，C 清空，Q/Esc 退出。")


    try:
        while True:
            ok, frame = capture.read()
            if not ok or frame is None:
                print("摄像头读取中断，程序已退出。请关闭占用摄像头的软件后重试。")
                break

            frame = cv2.flip(frame, 1)
            hands = tracker.process(frame)
            gesture_state = engine.update(hands, frame.shape)

            composed = renderer.build_base_frame(frame, gesture_state.framing_rect if gesture_state.framing_active else None)
            palette_rects = renderer.draw_palette(composed, paint_layer)

            if gesture_state.painting_active and gesture_state.brush_point is not None:
                if paint_layer.update_color_from_point(gesture_state.brush_point, palette_rects):
                    paint_layer.end_stroke()
                else:
                    if paint_layer.last_point is None or distance(paint_layer.last_point, gesture_state.brush_point) >= config.MIN_DRAW_DISTANCE:
                        paint_layer.stroke(gesture_state.brush_point)
            else:
                paint_layer.end_stroke()

            composed = paint_layer.composite(composed)
            renderer.draw_brush_cursor(composed, gesture_state.brush_point if gesture_state.painting_active else None, paint_layer)
            renderer.draw_status(composed, gesture_state, paint_layer, engine.brush_gesture_mode)
            renderer.draw_landmarks(composed, hands, gesture_state)

            if hasattr(cv2, "getWindowImageRect"):
                _, _, display_width, display_height = cv2.getWindowImageRect(config.WINDOW_NAME)
                renderer.set_display_size(display_width, display_height)
            display_frame = renderer.prepare_display_frame(composed, fullscreen_enabled)
            cv2.imshow(config.WINDOW_NAME, display_frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key in (ord("c"), ord("C")):
                paint_layer.clear()
            if key in (ord(config.FULLSCREEN_KEY), ord(config.FULLSCREEN_KEY.upper())):
                fullscreen_enabled = not fullscreen_enabled
                _set_fullscreen(fullscreen_enabled)
            if key in (ord(config.BRUSH_GESTURE_KEY), ord(config.BRUSH_GESTURE_KEY.upper())):
                mode = engine.cycle_brush_gesture_mode()
                paint_layer.end_stroke()
                print(f"画笔手势已切换为：{mode}")
            if key in (ord(config.LANDMARK_KEY), ord(config.LANDMARK_KEY.upper())):
                renderer.cycle_landmark_style()
            if key in (ord(config.LANGUAGE_KEY), ord(config.LANGUAGE_KEY.upper())):
                renderer.cycle_language()
            if key in (ord(config.COLOR_MODE_KEY), ord(config.COLOR_MODE_KEY.upper())):
                renderer.cycle_color_mode()
            if paint_layer.set_palette_index_from_key(chr(key)):
                paint_layer.end_stroke()
    finally:
        tracker.close()
        capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
