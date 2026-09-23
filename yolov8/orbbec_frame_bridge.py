#!/usr/bin/env python3
"""把 Orbbec ROS 彩色图写到共享内存文件，供 conda 中的 YOLO 读取。

请用系统 Python 运行（先 conda deactivate），并已 source ROS。
"""

from __future__ import annotations

import argparse
import os
import tempfile
from pathlib import Path

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image


DEFAULT_TOPIC = "/camera/color/image_raw"
DEFAULT_OUTPUT = Path("/dev/shm/orbbec_color.jpg")


class FrameBridgeNode(Node):
    def __init__(self, topic: str, output: Path) -> None:
        super().__init__("orbbec_frame_bridge")
        self.bridge = CvBridge()
        self.output = output
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.sub = self.create_subscription(
            Image, topic, self.callback, qos_profile_sensor_data
        )
        self.get_logger().info(f"订阅: {topic}")
        self.get_logger().info(f"写出: {output}")

    def callback(self, msg: Image) -> None:
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        # 先写临时文件再替换，避免 YOLO 读到半截图片
        fd, tmp_name = tempfile.mkstemp(
            suffix=".jpg", dir=str(self.output.parent)
        )
        os.close(fd)
        tmp_path = Path(tmp_name)
        try:
            cv2.imwrite(str(tmp_path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            os.replace(tmp_path, self.output)
        finally:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Orbbec 图像桥接")
    parser.add_argument("--topic", default=DEFAULT_TOPIC)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    rclpy.init()
    node = FrameBridgeNode(args.topic, Path(args.output))
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
