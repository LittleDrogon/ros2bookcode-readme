#!/usr/bin/python3
"""订阅 Orbbec 彩色图，用 YOLOv8 笔模型发布识别结果。"""

import json
import math
import time
from typing import Dict, List

import rclpy
from cv_bridge import CvBridge
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image
from std_msgs.msg import String

from common import ANNOTATED_TOPIC, COLOR_TOPIC, DETECTION_TOPIC, setup_logger
from pen_detector import DEFAULT_MODEL, PenDetection, YoloV8PenDetector, draw_detections


class PenTracker:
    def __init__(self) -> None:
        self._next_id = 1
        self._tracks: Dict[int, dict] = {}

    def update(self, detections: List[PenDetection]) -> List[str]:
        events: List[str] = []
        used = set()
        for detection in detections:
            best_id = None
            best_dist = 100.0
            for track_id, track in self._tracks.items():
                if track_id in used:
                    continue
                dist = math.hypot(detection.center[0] - track["cx"], detection.center[1] - track["cy"])
                if dist < best_dist:
                    best_id = track_id
                    best_dist = dist
            if best_id is None:
                best_id = self._next_id
                self._next_id += 1
                events.append(
                    "新目标 #%d %s %s 置信度 %.0f%% 中心 (%.0f, %.0f)"
                    % (
                        best_id,
                        detection.type_name,
                        detection.color_name,
                        detection.confidence * 100,
                        detection.center[0],
                        detection.center[1],
                    )
                )
            else:
                previous = self._tracks[best_id]
                if previous["type"] != detection.type_key:
                    events.append(
                        "目标 #%d 类型更新: %s -> %s"
                        % (best_id, previous["type_name"], detection.type_name)
                    )
            detection.track_id = best_id
            used.add(best_id)
            self._tracks[best_id] = {
                "cx": detection.center[0],
                "cy": detection.center[1],
                "type": detection.type_key,
                "type_name": detection.type_name,
                "missing": 0,
            }

        lost = []
        for track_id, track in self._tracks.items():
            if track_id in used:
                continue
            track["missing"] += 1
            if track["missing"] > 8:
                events.append("目标 #%d %s 离开画面" % (track_id, track["type_name"]))
                lost.append(track_id)
        for track_id in lost:
            del self._tracks[track_id]
        return events


class PenDetectorNode(Node):
    def __init__(self) -> None:
        super().__init__("pen_detector")
        self.log = setup_logger("pen_detector")
        self.declare_parameter("image_topic", COLOR_TOPIC)
        self.declare_parameter("detection_topic", DETECTION_TOPIC)
        self.declare_parameter("annotated_topic", ANNOTATED_TOPIC)
        self.declare_parameter("min_confidence", 0.35)
        self.declare_parameter("model_path", str(DEFAULT_MODEL))

        self.image_topic = self.get_parameter("image_topic").get_parameter_value().string_value
        self.detection_topic = self.get_parameter("detection_topic").get_parameter_value().string_value
        self.annotated_topic = self.get_parameter("annotated_topic").get_parameter_value().string_value
        self.min_confidence = self.get_parameter("min_confidence").get_parameter_value().double_value
        self.model_path = self.get_parameter("model_path").get_parameter_value().string_value

        self.bridge = CvBridge()
        self.tracker = PenTracker()
        self.fps_window_start = time.monotonic()
        self.fps_window_count = 0
        self.warned_no_image = False
        self.seen_frame = False

        self.yolo = YoloV8PenDetector(
            model_path=self.model_path,
            conf_threshold=self.min_confidence,
        )

        self.image_sub = self.create_subscription(
            Image, self.image_topic, self._on_image, qos_profile_sensor_data
        )
        self.detection_pub = self.create_publisher(String, self.detection_topic, 10)
        self.annotated_pub = self.create_publisher(Image, self.annotated_topic, qos_profile_sensor_data)
        self.create_timer(5.0, self._watchdog)

        self.log.info("笔识别节点已启动")
        self.log.info("检测引擎: YOLOv8n(微调) + OpenCV")
        self.log.info("模型: %s", self.model_path)
        self.log.info("推理设备: %s", self.yolo.provider)
        self.log.info("订阅: %s", self.image_topic)
        self.log.info("发布识别结果: %s", self.detection_topic)
        self.log.info("发布标注图像: %s", self.annotated_topic)
        self.log.info("可识别: 仅青色笔（铅笔/圆珠笔/中性笔/钢笔）")

    def _watchdog(self) -> None:
        if self.seen_frame:
            return
        if not self.warned_no_image:
            self.warned_no_image = True
            self.log.warning(
                "还没有收到图像。请先启动 Gemini 335L，并确认 %s 正在发布",
                self.image_topic,
            )

    def _on_image(self, msg: Image) -> None:
        self.fps_window_count += 1
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            if not self.seen_frame:
                self.seen_frame = True
                self.log.info(
                    "收到首帧 encoding=%s %dx%d",
                    msg.encoding,
                    msg.width,
                    msg.height,
                )
            detections = self.yolo.detect(frame)
            events = self.tracker.update(detections)
            annotated = draw_detections(frame, detections)
            self._publish(msg, detections, annotated)
            for event in events:
                self.log.info(event)
            self._log_fps(time.monotonic(), detections)
        except Exception:
            self.log.exception("处理图像失败")

    def _publish(self, src: Image, detections: List[PenDetection], annotated) -> None:
        pens = [item.to_dict() for item in detections]
        summary = "；".join(
            "#%s %s(%s, %.0f%%)"
            % (item["id"], item["type"], item["color"], item["confidence"] * 100)
            for item in pens
        )
        if not summary:
            summary = "未发现笔"
        payload = {
            "frame_id": src.header.frame_id,
            "stamp_sec": int(src.header.stamp.sec),
            "stamp_nanosec": int(src.header.stamp.nanosec),
            "count": len(pens),
            "engine": "yolov8n_pen+opencv",
            "summary": summary,
            "pens": pens,
        }
        text = String()
        text.data = json.dumps(payload, ensure_ascii=False)
        self.detection_pub.publish(text)

        out = self.bridge.cv2_to_imgmsg(annotated, encoding="bgr8")
        out.header = src.header
        self.annotated_pub.publish(out)

    def _log_fps(self, now: float, detections: List[PenDetection]) -> None:
        elapsed = now - self.fps_window_start
        if elapsed < 10.0:
            return
        fps = self.fps_window_count / elapsed
        names = "、".join(f"#{item.track_id}{item.type_name}" for item in detections) or "无"
        self.log.info("运行中 帧率 %.1f 当前 %d 支: %s", fps, len(detections), names)
        self.fps_window_start = now
        self.fps_window_count = 0


def main() -> None:
    rclpy.init()
    node = PenDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.log.info("检测节点收到退出信号")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
