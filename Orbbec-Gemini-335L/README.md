# Orbbec Gemini 335L 本机使用说明

本机工作空间路径：

`/home/lyzn-robot/ros2bookcode/Orbbec-Gemini-335L/OrbbecSDK_ROS2`

相机型号：**Orbbec Gemini 335L**，对应启动文件：`gemini_330_series.launch.py`

## 注意事项

1. 终端提示符若带 `(base)`，先执行 `conda deactivate`，避免 ROS Humble 使用到 conda 的 Python 3.13。
2. 启动前建议把系统 Python 放在 PATH 前面：`export PATH="/usr/bin:$PATH"`。
3. 同一时刻只能有一个进程占用相机；若提示 `uvc_open failed`，说明相机已被占用。

## 启动相机

终端 1：

```bash
conda deactivate
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
source /home/lyzn-robot/ros2bookcode/Orbbec-Gemini-335L/OrbbecSDK_ROS2/install/setup.bash
cd /home/lyzn-robot/ros2bookcode/Orbbec-Gemini-335L/OrbbecSDK_ROS2
ros2 launch orbbec_camera gemini_330_series.launch.py
```

检查设备（相机未被占用时）：

```bash
ros2 run orbbec_camera list_devices_node
```

## 查看彩色图像

终端 2（相机已启动后）：

```bash
conda deactivate
export PATH="/usr/bin:$PATH"
source /opt/ros/humble/setup.bash
source /home/lyzn-robot/ros2bookcode/Orbbec-Gemini-335L/OrbbecSDK_ROS2/install/setup.bash
ros2 run rqt_image_view rqt_image_view /camera/color/image_raw
```

也可在窗口里手动选择其他话题，例如：

- `/camera/color/image_raw`
- `/camera/depth/image_raw`

## 常用话题

| 话题 | 说明 |
|------|------|
| `/camera/color/image_raw` | 彩色图像 |
| `/camera/depth/image_raw` | 深度图像 |
| `/camera/depth/points` | 点云 |

查看话题是否在发布：

```bash
ros2 topic list | grep camera
ros2 topic hz /camera/color/image_raw
```

## 识别笔（YOLOv8 + OpenCV）

相机启动后，另开终端：

```bash
conda deactivate
export PATH="/usr/bin:$PATH"
bash /home/lyzn-robot/ros2bookcode/Orbbec-Gemini-335L/pen_recognition/run_pen_recognition.sh
```

程序会订阅 `/camera/color/image_raw`，用微调后的 **YOLOv8n** 检测笔，并用 **OpenCV** 过滤出**青色**笔（铅笔 / 圆珠笔 / 中性笔 / 钢笔），再画框发布：

| 话题 | 说明 |
|------|------|
| `/pen_recognition/detections` | JSON 识别结果 |
| `/pen_recognition/image` | 画好框的图像 |

模型：`pen_recognition/models/yolov8n_pen.onnx`（由 `yolov8n.pt` 在笔类别上微调后导出）。日志在 `pen_recognition/logs/`。浅色桌面、笔身完整露出时更准确。

只看结果、不打开窗口时：

```bash
ros2 topic echo /pen_recognition/detections
```

## 停止与清理

在启动相机的终端按 `Ctrl+C`。若残留进程导致无法再次打开，可执行：

```bash
pkill -f gemini_330_series.launch.py
pkill -f component_container
```
