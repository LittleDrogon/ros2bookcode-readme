#!/bin/bash
# Panda MoveIt Tkinter 控制面板
# 先启动: ros2 launch moveit_resources_panda_moveit_config demo.launch.py

set -eo pipefail
export PATH="/usr/bin:${PATH:-}"
source /opt/ros/humble/setup.bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"
exec /usr/bin/python3 "${SCRIPT_DIR}/panda_moveit_gui.py"
