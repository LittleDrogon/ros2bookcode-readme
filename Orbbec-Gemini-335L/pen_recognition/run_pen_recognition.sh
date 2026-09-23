#!/bin/bash
# 订阅已启动的 Gemini 335L 彩色图，用 YOLOv8 识别笔。
# 相机请另开终端，按上级 README 启动 gemini_330_series.launch.py。

set -eo pipefail

export PATH="/usr/bin:${PATH:-}"
# ROS setup.bash 会引用未定义变量，不能在 set -u 下 source
source /opt/ros/humble/setup.bash
source /home/lyzn-robot/ros2bookcode/Orbbec-Gemini-335L/OrbbecSDK_ROS2/install/setup.bash

LAUNCH_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/launch/pen_recognition.launch.py"
exec ros2 launch "${LAUNCH_FILE}"
