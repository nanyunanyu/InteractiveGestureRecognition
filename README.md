# 交互式手势识别绘画

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-FF6F00)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D4?logo=windows&logoColor=white)
![PyInstaller](https://img.shields.io/badge/Build-PyInstaller-2D2D2D)

[English](README.en.md) | 中文

基于 OpenCV 与 MediaPipe 的 Windows 摄像头手势交互程序。程序会实时识别手部关键点，支持用手势框选画面区域、切换画笔/橡皮、在摄像头画面上进行交互式绘画。

## 目录

- [功能特性](#功能特性)
- [项目结构](#项目结构)
- [环境要求](#环境要求)
- [安装依赖](#安装依赖)
- [运行源码](#运行源码)
- [快捷键](#快捷键)
- [手势说明](#手势说明)
- [打包为 exe](#打包为-exe)
- [常见问题](#常见问题)
- [许可证](#许可证)

## 功能特性

- 实时摄像头画面采集与手部关键点识别
- 支持中文/英文界面切换
- 支持捏合、食指、混合三种绘画手势模式
- 支持双手框选区域高亮
- 支持红、绿、蓝、黄、白五种画笔颜色和橡皮擦
- 支持全屏显示、画布清空、关键点显示模式切换
- 已支持 PyInstaller 打包为 Windows `.exe`

## 项目结构

```text
.
├── src/
│   ├── main.py              # 程序入口
│   ├── config.py            # 参数配置
│   ├── gesture_engine.py    # 手势状态识别
│   ├── hand_tracker.py      # MediaPipe 手部追踪
│   ├── paint_layer.py       # 绘画图层
│   ├── renderer.py          # 界面渲染
│   └── utils.py             # 工具函数
├── app_icon.ico             # 软件图标
├── requirements.txt         # Python 依赖
├── README.md                # 中文说明
└── README.en.md             # English README
```

## 环境要求

- Windows 10/11
- Python 3.10 或更高版本
- 可用摄像头

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行源码

```bash
python src/main.py
```

启动后请允许程序访问摄像头。如果程序提示无法读取摄像头，可以关闭其他占用摄像头的软件后重试，或在 `src/config.py` 中将 `CAMERA_INDEX = 0` 改为 `CAMERA_INDEX = 1`。

## 快捷键

| 按键          | 功能                               |
| ----------- | -------------------------------- |
| `1` - `5`   | 切换画笔颜色                           |
| `6`         | 切换到橡皮擦                           |
| `G`         | 切换绘画手势模式：捏合 / 食指 / 混合            |
| `T`         | 切换中文 / 英文界面                      |
| `L`         | 切换手部关键点显示模式                      |
| `F`         | 切换全屏                             |
| `V`         | 切换画面颜色                           |
| `C`         | 清空画布                             |
| `Q` / `Esc` | 退出程序 |

## 手势说明

### 绘画

默认绘画手势为“捏合”：拇指与食指靠近时开始绘画，松开后停止绘画。也可以按 `G` 切换为“食指”或“混合”模式。

### 颜色选择

把绘画光标移动到左上角调色板并停留片刻，可以切换画笔颜色或橡皮擦。也可以直接使用数字键 `1` - `6` 快速切换。

### 框选区域

当检测到双手拇指与食指张开形成框选姿态时，程序会高亮双手之间的画面区域。

## 打包为 exe

项目已使用 PyInstaller 打包，生成文件位于：

```text
dist/InteractiveGestureRecognition.exe
```

如需重新打包，可执行：

```bash
python -m PyInstaller --noconfirm --clean --onefile --windowed \
  --name "InteractiveGestureRecognition" \
  --icon "app_icon.ico" \
  --paths "src" \
  --collect-data mediapipe \
  --collect-binaries mediapipe \
  "src/main.py"
```

打包完成后，`.exe` 文件会输出到 `dist/` 目录。

## 常见问题

### 程序打不开摄像头

- 检查 Windows 隐私设置中是否允许桌面应用访问摄像头
- 关闭微信、浏览器、会议软件等可能占用摄像头的程序
- 尝试在 `src/config.py` 中修改 `CAMERA_INDEX`

### exe 首次启动较慢

当前打包方式为单文件模式，首次启动时需要解压依赖文件，因此启动会稍慢一些。

### 杀毒软件误报

PyInstaller 打包的单文件程序偶尔会被杀毒软件误报。可以改用源码运行，或自行在本机重新打包。

## 许可证

本项目使用 MIT License 开源，详情请查看 [LICENSE](LICENSE) 文件。
