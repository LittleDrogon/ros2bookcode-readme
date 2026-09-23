#!/usr/bin/python3
"""用 Tkinter 订阅 YOLOv8 笔识别结果，显示画面、列表和日志。"""

import json
import logging
import queue
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
from tkinter import scrolledtext, ttk

import cv2
import rclpy
from cv_bridge import CvBridge
from PIL import Image, ImageTk
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image as RosImage
from std_msgs.msg import String

from common import ANNOTATED_TOPIC, DETECTION_TOPIC, LOG_FORMAT, setup_logger


class PenGuiNode(Node):
    def __init__(self, log_queue: "queue.Queue[str]") -> None:
        super().__init__("pen_recognition_gui")
        self.log = setup_logger("pen_gui")
        self.log_queue = log_queue
        self.log.addHandler(_QueueLogHandler(log_queue))

        self.declare_parameter("detection_topic", DETECTION_TOPIC)
        self.declare_parameter("annotated_topic", ANNOTATED_TOPIC)
        self.detection_topic = self.get_parameter("detection_topic").get_parameter_value().string_value
        self.annotated_topic = self.get_parameter("annotated_topic").get_parameter_value().string_value

        self.bridge = CvBridge()
        self.lock = threading.Lock()
        self.latest_image = None
        self.latest_result = None
        self.seen_image = False
        self.seen_result = False
        self.last_summary = ""
        self.frame_times = []

        self.create_subscription(RosImage, self.annotated_topic, self._on_image, qos_profile_sensor_data)
        self.create_subscription(String, self.detection_topic, self._on_result, 10)
        self.log.info("界面节点已启动")
        self.log.info("订阅标注图像: %s", self.annotated_topic)
        self.log.info("订阅识别结果: %s", self.detection_topic)

    def _on_image(self, msg: RosImage) -> None:
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except Exception:
            self.log.exception("标注图像转换失败")
            return
        now = time.monotonic()
        with self.lock:
            self.latest_image = frame
            self.frame_times.append(now)
            self.frame_times = [item for item in self.frame_times if now - item < 2.0]
            first = not self.seen_image
            self.seen_image = True
        if first:
            self.log.info("收到标注图像 %dx%d", msg.width, msg.height)

    def _on_result(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except json.JSONDecodeError:
            self.log.error("识别结果不是合法 JSON: %s", msg.data[:200])
            return
        summary = str(payload.get("summary", ""))
        with self.lock:
            self.latest_result = payload
            changed = summary != self.last_summary
            self.last_summary = summary
            first = not self.seen_result
            self.seen_result = True
        if first or changed:
            count = payload.get("count", 0)
            engine = payload.get("engine", "yolov8")
            self.log.info("识别结果[%s]: %d 支 | %s", engine, count, summary)

    def snapshot(self):
        with self.lock:
            image = None if self.latest_image is None else self.latest_image.copy()
            result = None if self.latest_result is None else dict(self.latest_result)
            fps = 0.0
            if len(self.frame_times) >= 2:
                span = self.frame_times[-1] - self.frame_times[0]
                if span > 0:
                    fps = (len(self.frame_times) - 1) / span
            return image, result, fps


class _QueueLogHandler(logging.Handler):
    def __init__(self, log_queue: "queue.Queue[str]") -> None:
        super().__init__()
        self.log_queue = log_queue
        self.setFormatter(logging.Formatter(LOG_FORMAT))

    def emit(self, record: logging.LogRecord) -> None:
        self.log_queue.put(self.format(record))


class PenApp:
    def __init__(self, node: PenGuiNode, log_queue: "queue.Queue[str]") -> None:
        self.node = node
        self.log_queue = log_queue
        self.photo = None

        self.root = tk.Tk()
        self.root.title("Orbbec Gemini 335L 笔识别 (YOLOv8)")
        self.root.geometry("1280x760")
        self.root.minsize(960, 640)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        family = _cjk_family(self.root)
        self.font = tkfont.Font(family=family, size=11)
        self.font_small = tkfont.Font(family=family, size=10)
        self.root.option_add("*Font", self.font)

        self._build()
        self.root.after(60, self._refresh)

    def _build(self) -> None:
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)

        left = ttk.Frame(self.root, padding=8)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)
        ttk.Label(left, text="相机画面（YOLOv8 标注）").grid(row=0, column=0, sticky="w")
        self.canvas = tk.Canvas(left, bg="#1e1e1e", highlightthickness=0, width=860, height=540)
        self.canvas.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        self.canvas.create_text(
            430,
            270,
            text="等待标注图像\n/pen_recognition/image",
            fill="#dddddd",
            font=self.font,
            justify="center",
        )

        right = ttk.Frame(self.root, padding=8)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(2, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="识别结果").grid(row=0, column=0, sticky="w")
        columns = ("id", "type", "color", "conf", "center", "size")
        self.tree = ttk.Treeview(right, columns=columns, show="headings", height=8)
        headings = {
            "id": "编号",
            "type": "类型",
            "color": "颜色",
            "conf": "置信度",
            "center": "中心",
            "size": "框大小",
        }
        widths = {"id": 50, "type": 70, "color": 60, "conf": 70, "center": 110, "size": 90}
        for key in columns:
            self.tree.heading(key, text=headings[key])
            self.tree.column(key, width=widths[key], anchor="center")
        self.tree.grid(row=1, column=0, sticky="ew", pady=(6, 8))

        log_bar = ttk.Frame(right)
        log_bar.grid(row=2, column=0, sticky="nsew")
        log_bar.rowconfigure(1, weight=1)
        log_bar.columnconfigure(0, weight=1)
        header = ttk.Frame(log_bar)
        header.grid(row=0, column=0, sticky="ew")
        ttk.Label(header, text="日志").pack(side="left")
        ttk.Button(header, text="清空日志", command=self._clear_log).pack(side="right")
        self.log_view = scrolledtext.ScrolledText(log_bar, height=16, state="disabled", font=self.font_small)
        self.log_view.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        self.log_view.tag_config("WARNING", foreground="#a15c00")
        self.log_view.tag_config("ERROR", foreground="#b00020")

        hint = "只识别青色笔。引擎：微调 YOLOv8n + OpenCV 颜色过滤。浅色桌面、笔身完整露出时效果更好。"
        ttk.Label(right, text=hint, wraplength=420, foreground="#444444").grid(row=3, column=0, sticky="w", pady=(8, 0))

        self.status = ttk.Label(self.root, anchor="w", padding=(8, 4))
        self.status.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status.configure(text="正在连接话题…")

    def _refresh(self) -> None:
        try:
            self._drain_logs()
            image, result, fps = self.node.snapshot()
            if image is not None:
                self._show_image(image)
            self._show_result(result)
            count = 0 if not result else int(result.get("count", 0))
            summary = "等待识别结果" if result is None else result.get("summary", "")
            image_state = "无画面" if image is None else f"{image.shape[1]}×{image.shape[0]}"
            engine = "" if not result else f"  [{result.get('engine', 'yolov8')}]"
            self.status.configure(
                text=f"画面 {image_state}    帧率 {fps:.1f}    笔 {count}{engine}    {summary}"
            )
        except Exception:
            self.node.log.exception("界面刷新失败")
        if self.root.winfo_exists():
            self.root.after(60, self._refresh)

    def _show_image(self, frame) -> None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb)
        width = max(self.canvas.winfo_width(), 640)
        height = max(self.canvas.winfo_height(), 360)
        pil_image.thumbnail((width, height), Image.BILINEAR)
        self.photo = ImageTk.PhotoImage(pil_image)
        self.canvas.delete("all")
        self.canvas.create_image(width // 2, height // 2, image=self.photo)

    def _show_result(self, result) -> None:
        current = self.tree.get_children()
        if current:
            self.tree.delete(*current)
        if not result:
            return
        for pen in result.get("pens", []):
            center = pen.get("center", [0, 0])
            self.tree.insert(
                "",
                "end",
                values=(
                    pen.get("id", ""),
                    pen.get("type", ""),
                    pen.get("color", ""),
                    f"{float(pen.get('confidence', 0)) * 100:.0f}%",
                    f"({center[0]:.0f}, {center[1]:.0f})",
                    f"{pen.get('length_px', 0):.0f}×{pen.get('width_px', 0):.0f}",
                ),
            )

    def _drain_logs(self) -> None:
        lines = []
        while True:
            try:
                lines.append(self.log_queue.get_nowait())
            except queue.Empty:
                break
        if not lines:
            return
        self.log_view.configure(state="normal")
        for line in lines:
            tag = None
            if " WARNING " in f" {line} ":
                tag = "WARNING"
            elif " ERROR " in f" {line} ":
                tag = "ERROR"
            if tag:
                self.log_view.insert("end", line + "\n", tag)
            else:
                self.log_view.insert("end", line + "\n")
        line_count = int(self.log_view.index("end-1c").split(".")[0])
        if line_count > 400:
            self.log_view.delete("1.0", f"{line_count - 400}.0")
        self.log_view.see("end")
        self.log_view.configure(state="disabled")

    def _clear_log(self) -> None:
        self.log_view.configure(state="normal")
        self.log_view.delete("1.0", "end")
        self.log_view.configure(state="disabled")
        self.node.log.info("界面日志已清空（日志文件仍保留）")

    def close(self) -> None:
        self.node.log.info("关闭笔识别界面")
        self.root.quit()

    def run(self) -> None:
        self.root.mainloop()


def _cjk_family(root: tk.Tk) -> str:
    families = set(tkfont.families(root))
    for name in ("Noto Sans CJK SC", "Noto Sans CJK JP", "Droid Sans Fallback", "WenQuanYi Micro Hei"):
        if name in families:
            return name
    return "Sans"


def main() -> None:
    log_queue: "queue.Queue[str]" = queue.Queue()
    rclpy.init()
    node = PenGuiNode(log_queue)
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()
    app = PenApp(node, log_queue)
    try:
        app.run()
    finally:
        node.log.info("界面节点退出")
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
