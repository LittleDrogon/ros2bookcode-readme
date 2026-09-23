# YOLOv8 物体检测

本目录使用本地权重 `yolov8n.pt`，对图片、视频或 **Orbbec Gemini 335L** 画面做物体检测。

## 环境

| 场景 | Python |
|------|--------|
| 图片 / 视频 | conda：`python` 或 `/home/lyzn-robot/miniconda3/bin/python` |
| Orbbec 实时检测 | conda 跑 YOLO；系统 Python 跑 ROS 图像桥接 |

## 快速开始（图片 / 视频）

```bash
cd /home/lyzn-robot/ros2bookcode/yolov8

# 检测图片并保存
python detect.py --source bus.jpg --save

# 检测视频并保存
python detect.py --source your.mp4 --save

# Orbbec 直接用 OpenCV（不要用 0）
# video0=深度, video6=彩色 YUYV
python detect.py --source 6
```

结果在 `runs/detect/`。窗口中按 `q` 退出。

`QFontDatabase: Cannot find font directory ... cv2/qt/fonts` 是字体警告，可忽略。

## Orbbec 相机实时检测

### 方式 A：直接读彩色设备（简单）

确认没有占用相机的 `ros2 launch` 后：

```bash
cd /home/lyzn-robot/ros2bookcode/yolov8
python detect.py --source 6
```

### 方式 B：走 ROS 话题（相机已被 launch 占用时）

**不要**再使用 `python detect.py --source 0`（0 是深度节点，且常被占用）。

请按下面 3 个终端操作：

**终端 1：启动相机**

```bash
conda deactivate
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
source /home/lyzn-robot/ros2bookcode/Orbbec-Gemini-335L/OrbbecSDK_ROS2/install/setup.bash
ros2 launch orbbec_camera gemini_330_series.launch.py
```

**终端 2：ROS 图像桥接（系统 Python）**

```bash
conda deactivate
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
source /home/lyzn-robot/ros2bookcode/Orbbec-Gemini-335L/OrbbecSDK_ROS2/install/setup.bash
cd /home/lyzn-robot/ros2bookcode/yolov8
python3 orbbec_frame_bridge.py
```

**终端 3：YOLOv8 检测（conda / GPU）**

```bash
cd /home/lyzn-robot/ros2bookcode/yolov8
python detect_orbbec.py
```

窗口中按 `q` 退出。常用参数：

```bash
python detect_orbbec.py --conf 0.5 --device 0
python detect_orbbec.py --noshow
```

## detect.py 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--weights` | 同目录 `yolov8n.pt` | 模型权重 |
| `--source` | `6` | 图片/视频路径，或摄像头编号；Orbbec 彩色用 `6` |
| `--conf` | `0.25` | 置信度阈值 |
| `--device` | `0` | `0`=GPU，`cpu`=CPU |
| `--save` | 关闭 | 保存到 `runs/detect/` |
| `--noshow` | 关闭 | 不弹窗 |

## 常见问题

### `Failed to open 0` / `can't open camera by index`

Orbbec 的 `/dev/video0` 是**深度流**，不是彩色。请改用：

```bash
python detect.py --source 6
```

若已经 `ros2 launch orbbec_camera ...`，设备会被占用，请改用方式 B（三终端）。

### `QFontDatabase: Cannot find font directory ... cv2/qt/fonts`

OpenCV 字体警告，可忽略，不影响检测。

### `ModuleNotFoundError: rclpy._rclpy_pybind11`

终端还在用 conda 的 Python。桥接脚本需要：`conda deactivate` 后再 `export PATH="/usr/bin:$PATH"`。

## 文件说明

- `yolov8n.pt`：YOLOv8n 权重
- `detect.py`：图片 / 视频 / 普通摄像头检测
- `orbbec_frame_bridge.py`：把 ROS 彩色图写到 `/dev/shm/orbbec_color.jpg`
- `detect_orbbec.py`：读取桥接图像并做 YOLO 检测
- `detect_orbbec_ros.py`：单进程 ROS+YOLO（需系统 Python 另装 ultralytics）
- `runs/detect/`：`detect.py --save` 输出目录
