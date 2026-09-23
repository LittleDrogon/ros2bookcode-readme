#!/usr/bin/env python3
"""YOLOv8 物体检测脚本：支持图片 / 视频 / 摄像头。"""

from __future__ import annotations

import argparse
from pathlib import Path

from ultralytics import YOLO


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_WEIGHTS = SCRIPT_DIR / "yolov8n.pt"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="YOLOv8 物体检测")
    parser.add_argument(
        "--weights",
        type=str,
        default=str(DEFAULT_WEIGHTS),
        help="模型权重路径，默认使用同目录下的 yolov8n.pt",
    )
    parser.add_argument(
        "--source",
        type=str,
        default="6",
        help="检测源：图片/视频路径，或摄像头编号。"
        " Orbbec Gemini 335L 彩色流一般是 6（0 是深度，打不开彩色）",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.25,
        help="置信度阈值，默认 0.25",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="0",
        help="推理设备：0=第一块 GPU，cpu=仅 CPU",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="保存检测结果到 runs/detect/",
    )
    parser.add_argument(
        "--noshow",
        action="store_true",
        help="不弹出显示窗口（适合无界面环境）",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    weights = Path(args.weights)
    if not weights.is_file():
        raise FileNotFoundError(f"找不到权重文件: {weights}")

    # 摄像头编号转 int，其他路径保持字符串
    source: str | int = int(args.source) if args.source.isdigit() else args.source

    if isinstance(source, int) and source == 0:
        print(
            "提示: Orbbec 的 /dev/video0 是深度流，不是彩色。"
            "请改用: python detect.py --source 6"
        )

    model = YOLO(str(weights))
    try:
        results = model.predict(
            source=source,
            conf=args.conf,
            device=args.device,
            show=not args.noshow,
            save=args.save,
            stream=True,
        )

        for result in results:
            names = result.names
            boxes = result.boxes
            if boxes is None or len(boxes) == 0:
                print("未检测到目标")
                continue

            print(f"检测到 {len(boxes)} 个目标:")
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()
                print(
                    f"  - {names[cls_id]:16s} "
                    f"conf={conf:.2f}  "
                    f"box=[{xyxy[0]:.0f}, {xyxy[1]:.0f}, {xyxy[2]:.0f}, {xyxy[3]:.0f}]"
                )
    except ConnectionError as exc:
        print(f"打开摄像头失败: {exc}")
        print("Orbbec Gemini 335L 请使用彩色节点:")
        print("  python detect.py --source 6")
        print("若相机已被 ros2 launch 占用，请改用 README 里的三终端方案。")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
