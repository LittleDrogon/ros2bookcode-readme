"""同时启动 YOLOv8 笔识别节点和 Tkinter 界面。"""

import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess

PYTHON = "/usr/bin/python3"
PACKAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def generate_launch_description() -> LaunchDescription:
    env = {"PYTHONUNBUFFERED": "1"}
    detector = os.path.join(PACKAGE_DIR, "detector_node.py")
    gui = os.path.join(PACKAGE_DIR, "gui_node.py")
    return LaunchDescription(
        [
            ExecuteProcess(cmd=[PYTHON, detector], output="screen", additional_env=env),
            ExecuteProcess(cmd=[PYTHON, gui], output="screen", additional_env=env),
        ]
    )
