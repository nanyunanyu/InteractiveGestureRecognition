WINDOW_NAME = "Interactive Gesture Recognition"
CAMERA_INDEX = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

DEFAULT_FULLSCREEN = False
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 720
FULLSCREEN_SCALE_MODE = "stretch"
FULLSCREEN_KEY = "f"

COLOR_MODES = ["grayscale", "color"]
COLOR_MODE = "grayscale"
COLOR_MODE_KEY = "v"

LANGUAGE = "zh"
LANGUAGES = ["zh", "en"]
LANGUAGE_KEY = "t"
FONT_PATHS = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
]

FRAMING_MIN_SPREAD_RATIO = 0.42
FRAMING_KEEP_SPREAD_RATIO = 0.32
FRAMING_MIN_WIDTH = 120
FRAMING_MIN_HEIGHT = 80
FRAMING_ASPECT_MIN = 0.25
FRAMING_ASPECT_MAX = 8.0
FRAMING_PADDING_RATIO = 0.16
FRAMING_ENTER_FRAMES = 2
FRAMING_EXIT_FRAMES = 8
RECT_SMOOTHING = 0.42

BRUSH_GESTURE_MODES = ["pinch", "index", "both"]
BRUSH_GESTURE_MODE = "pinch"
BRUSH_GESTURE_KEY = "g"

PINCH_START_RATIO = 0.35
PINCH_END_RATIO = 0.45
PINCH_ENTER_FRAMES = 2
PINCH_EXIT_FRAMES = 2

INDEX_ENTER_FRAMES = 2
INDEX_EXIT_FRAMES = 3
INDEX_EXTEND_RATIO = 1.12
INDEX_MIN_ANGLE = 150
OTHER_FINGER_FOLDED_RATIO = 1.05

POINT_SMOOTHING = 0.35
MIN_DRAW_DISTANCE = 3

BRUSH_THICKNESS = 8
ERASER_THICKNESS = 20

PALETTE_BOX_WIDTH = 58
PALETTE_BOX_HEIGHT = 38
PALETTE_GAP = 10
PALETTE_MARGIN = 18
PALETTE_HOVER_FRAMES = 10

LANDMARK_STYLES = ["minimal", "full", "off"]
LANDMARK_STYLE = "minimal"
LANDMARK_KEY = "l"

UI_PANEL_COLOR = (18, 22, 30)
UI_PANEL_ALPHA = 0.72
UI_TEXT_COLOR = (245, 245, 245)
UI_MUTED_TEXT_COLOR = (170, 178, 190)
UI_ACCENT_COLOR = (255, 210, 80)
UI_SUCCESS_COLOR = (80, 220, 140)
UI_FRAME_COLOR = (255, 190, 60)
UI_DANGER_COLOR = (70, 90, 255)
UI_MARGIN = 18
UI_STATUS_HEIGHT = 66

PALETTE = [
    {"name": "Red", "zh_name": "红色", "color": (0, 0, 255), "key": "1", "eraser": False},
    {"name": "Green", "zh_name": "绿色", "color": (0, 210, 80), "key": "2", "eraser": False},
    {"name": "Blue", "zh_name": "蓝色", "color": (255, 140, 0), "key": "3", "eraser": False},
    {"name": "Yellow", "zh_name": "黄色", "color": (0, 220, 255), "key": "4", "eraser": False},
    {"name": "White", "zh_name": "白色", "color": (255, 255, 255), "key": "5", "eraser": False},
    {"name": "Eraser", "zh_name": "橡皮", "color": (0, 0, 0), "key": "6", "eraser": True},
]
