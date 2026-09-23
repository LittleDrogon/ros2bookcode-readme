#!/bin/bash
# 控制已启动的 Panda MoveIt 仿真。
# 终端 1: ros2 launch moveit_resources_panda_moveit_config demo.launch.py
# 终端 2: 运行本脚本

set -eo pipefail
export PATH="/usr/bin:${PATH:-}"
source /opt/ros/humble/setup.bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec /usr/bin/python3 "${SCRIPT_DIR}/panda_moveit_demo.py"
