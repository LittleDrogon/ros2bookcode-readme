#!/usr/bin/env python3
"""订阅 Orbbec 彩色图话题，用 YOLOv8 实时检测。

依赖：
1. 先启动相机：ros2 launch orbbec_camera gemini_330_series.launch.py
2. 使用系统 Python（不要用 conda），并已 source ROS 环境
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from ultralytics import YOLO


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_WEIGHTS = SCRIPT_DIR / "yolov8n.pt"
DEFAULT_TOPIC = "/camera/color/image_raw"


class YoloOrbbecNode(Node):
    def __init__(
        self,
        weights: Path,
        topic: str,
        conf: float,
        device: str,
        show: bool,
    ) -> None:
        super().__init__("yolo_orbbec_detect")
        self.bridge = CvBridge()
        self.conf = conf
        self.device = device
        self.show = show
        self.model = YOLO(str(weights))
        self.sub = self.create_subscription(
            Image, topic, self.image_callback, qos_profile_sensor_data
        )
        self.get_logger().info(f"已加载模型: {weights}")
        self.get_logger().info(f"订阅话题: {topic}")
        self.get_logger().info("按 q 退出显示窗口")

    def image_callback(self, msg: Image) -> None:
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        results = self.model.predict(
            source=frame,
            conf=self.conf,
            device=self.device,
            verbose=False,
        )
        result = results[0]
        annotated = result.plot()

        boxes = result.boxes
        if boxes is not None and len(boxes) > 0:
            names = result.names
            summary = ", ".join(
                f"{names[int(b.cls[0])]}:{float(b.conf[0]):.2f}" for b in boxes
            )
            self.get_logger().info(f"检测到 {len(boxes)} 个目标: {summary}")
        else:
            self.get_logger().info("未检测到目标")

        if self.show:
            cv2.imshow("YOLOv8 Orbbec", annotated)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                self.get_logger().info("收到退出键，关闭节点")
                raise SystemExit(0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Orbbec + YOLOv8 实时检测")
    parser.add_argument(
        "--weights",
        type=str,
        default=str(DEFAULT_WEIGHTS),
        help="模型权重路径，默认同目录 yolov8n.pt",
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=DEFAULT_TOPIC,
        help="彩色图像话题",
    )
    parser.add_argument("--conf", type=float, default=0.25, help="置信度阈值")
    parser.add_argument(
        "--device",
        type=str,
        default="0",
        help="推理设备：0=GPU，cpu=CPU",
    )
    parser.add_argument(
        "--noshow",
        action="store_true",
        help="不弹出显示窗口",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    weights = Path(args.weights)
    if not weights.is_file():
        raise FileNotFoundError(f"找不到权重文件: {weights}")

    rclpy.init()
    node = YoloOrbbecNode(
        weights=weights,
        topic=args.topic,
        conf=args.conf,
        device=args.device,
        show=not args.noshow,
    )
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
