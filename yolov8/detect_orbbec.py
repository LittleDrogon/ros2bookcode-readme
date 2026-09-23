#!/usr/bin/env python3
"""读取 Orbbec 桥接图像，用 YOLOv8 实时检测。

配合 orbbec_frame_bridge.py 使用，可在 conda 环境下运行（支持 GPU）。
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
from ultralytics import YOLO


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_WEIGHTS = SCRIPT_DIR / "yolov8n.pt"
DEFAULT_SOURCE = Path("/dev/shm/orbbec_color.jpg")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 检测 Orbbec 桥接图像")
    parser.add_argument("--weights", default=str(DEFAULT_WEIGHTS))
    parser.add_argument("--source", default=str(DEFAULT_SOURCE), help="桥接输出的图片路径")
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--device", default="0")
    parser.add_argument("--noshow", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    weights = Path(args.weights)
    source = Path(args.source)
    if not weights.is_file():
        raise FileNotFoundError(f"找不到权重文件: {weights}")

    model = YOLO(str(weights))
    print(f"模型: {weights}")
    print(f"等待图像: {source}")
    print("按 q 退出")

    last_mtime = None
    while True:
        if not source.is_file():
            time.sleep(0.05)
            continue

        mtime = source.stat().st_mtime
        if last_mtime is not None and mtime == last_mtime:
            time.sleep(0.01)
            continue
        last_mtime = mtime

        frame = cv2.imread(str(source))
        if frame is None:
            continue

        results = model.predict(
            source=frame,
            conf=args.conf,
            device=args.device,
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
            print(f"检测到 {len(boxes)} 个目标: {summary}")
        else:
            print("未检测到目标")

        if not args.noshow:
            cv2.imshow("YOLOv8 Orbbec", annotated)
            if (cv2.waitKey(1) & 0xFF) == ord("q"):
                break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
