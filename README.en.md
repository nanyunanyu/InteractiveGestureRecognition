# Interactive Gesture Recognition Drawing

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-FF6F00)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D4?logo=windows&logoColor=white)
![PyInstaller](https://img.shields.io/badge/Build-PyInstaller-2D2D2D)

English | [中文](README.md)

A Windows camera-based gesture interaction application built with OpenCV and MediaPipe. It recognizes hand landmarks in real time and supports gesture-based area selection, brush/eraser switching, and interactive drawing directly on the camera feed.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Install Dependencies](#install-dependencies)
- [Run From Source](#run-from-source)
- [Shortcuts](#shortcuts)
- [Gesture Guide](#gesture-guide)
- [Package as exe](#package-as-exe)
- [FAQ](#faq)
- [License](#license)

## Features

- Real-time camera capture and hand landmark recognition
- Chinese/English interface switching
- Three drawing gesture modes: pinch, index finger, and hybrid
- Two-hand rectangular area highlight
- Five brush colors: red, green, blue, yellow, and white, plus an eraser
- Full-screen mode, canvas clearing, and hand landmark display toggling
- PyInstaller packaging support for Windows `.exe`

## Project Structure

```text
.
├── src/
│   ├── main.py              # Application entry point
│   ├── config.py            # Parameter configuration
│   ├── gesture_engine.py    # Gesture state recognition
│   ├── hand_tracker.py      # MediaPipe hand tracking
│   ├── paint_layer.py       # Drawing layer
│   ├── renderer.py          # UI rendering
│   └── utils.py             # Utility functions
├── app_icon.ico             # Application icon
├── requirements.txt         # Python dependencies
├── README.md                # Chinese README
└── README.en.md             # English README
```

## Requirements

- Windows 10/11
- Python 3.10 or later
- A working camera

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run From Source

```bash
python src/main.py
```

After startup, allow the application to access the camera. If the program reports that it cannot read the camera, close other software that may be using the camera and try again, or change `CAMERA_INDEX = 0` to `CAMERA_INDEX = 1` in `src/config.py`.

## Shortcuts

| Key         | Action                                      |
| ----------- | ------------------------------------------- |
| `1` - `5`   | Switch brush color                          |
| `6`         | Switch to eraser                            |
| `G`         | Switch drawing gesture mode: pinch / index / hybrid |
| `T`         | Switch Chinese / English interface          |
| `L`         | Toggle hand landmark display mode           |
| `F`         | Toggle full screen                          |
| `V`         | Toggle frame color                          |
| `C`         | Clear canvas                                |
| `Q` / `Esc` | Exit the application                        |

## Gesture Guide

### Drawing

The default drawing gesture is "pinch": drawing starts when the thumb and index finger move close together, and stops when they separate. You can also press `G` to switch to "index finger" or "hybrid" mode.

### Color Selection

Move the drawing cursor to the palette in the upper-left corner and pause briefly to switch the brush color or eraser. You can also use number keys `1` - `6` for quick switching.

### Area Selection

When both hands are detected with the thumb and index finger spread into a rectangular selection pose, the application highlights the image area between the two hands.

## Package as exe

The project has been packaged with PyInstaller. The generated file is located at:

```text
dist/InteractiveGestureRecognition.exe
```

To rebuild the executable, run:

```bash
python -m PyInstaller --noconfirm --clean --onefile --windowed \
  --name "InteractiveGestureRecognition" \
  --icon "app_icon.ico" \
  --paths "src" \
  --collect-data mediapipe \
  --collect-binaries mediapipe \
  "src/main.py"
```

After packaging completes, the `.exe` file will be output to the `dist/` directory.

## FAQ

### The application cannot open the camera

- Check whether Windows privacy settings allow desktop apps to access the camera
- Close WeChat, browsers, meeting software, or any other applications that may be using the camera
- Try changing `CAMERA_INDEX` in `src/config.py`

### The exe starts slowly the first time

The current package uses single-file mode. On first launch, it needs to extract dependency files, so startup may be slightly slower.

### Antivirus false positive

Single-file applications packaged with PyInstaller may occasionally be flagged by antivirus software. You can run from source instead, or rebuild the executable locally.

## License

If you plan to publish this project as open source, add a license file according to your needs, such as the MIT License.
