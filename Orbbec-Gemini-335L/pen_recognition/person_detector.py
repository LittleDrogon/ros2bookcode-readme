"""用人检测：YOLOv8（ONNX）推理 + OpenCV 预处理/后处理/画框。

模型来自本机 yolov8n.pt 导出的 yolov8n.onnx（COCO，类别 0=person）。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"
PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = PACKAGE_DIR / "models" / "yolov8n.onnx"
# 仓库里原始权重，便于对照说明
DEFAULT_PT = Path("/home/lyzn-robot/ros2bookcode/yolov8/yolov8n.pt")

PERSON_CLASS_ID = 0
TYPE_PERSON = "person"
TYPE_NAMES = {TYPE_PERSON: "人"}
BOX_COLOR = (40, 220, 40)


@dataclass
class PersonDetection:
    type_key: str
    type_name: str
    color_name: str
    confidence: float
    box: np.ndarray
    center: Tuple[float, float]
    angle_deg: float
    length_px: float
    width_px: float
    bbox: Tuple[int, int, int, int]
    track_id: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "id": self.track_id,
            "type": self.type_name,
            "type_key": self.type_key,
            "color": self.color_name,
            "confidence": round(float(self.confidence), 2),
            "bbox": [int(v) for v in self.bbox],
            "center": [round(float(self.center[0]), 1), round(float(self.center[1]), 1)],
            "angle_deg": round(float(self.angle_deg), 1),
            "length_px": round(float(self.length_px), 1),
            "width_px": round(float(self.width_px), 1),
        }


class YoloV8PersonDetector:
    """YOLOv8n ONNX 仅输出 person；OpenCV 负责 letterbox / NMS / 画框。"""

    def __init__(
        self,
        model_path: Path | str = DEFAULT_MODEL,
        conf_threshold: float = 0.35,
        iou_threshold: float = 0.45,
        imgsz: int = 640,
    ) -> None:
        self.model_path = Path(model_path)
        if not self.model_path.is_file():
            raise FileNotFoundError(
                f"找不到 YOLOv8 ONNX 模型: {self.model_path}\n"
                f"请先用 conda 导出: YOLO('{DEFAULT_PT}').export(format='onnx')"
            )
        self.conf_threshold = float(conf_threshold)
        self.iou_threshold = float(iou_threshold)
        self.imgsz = int(imgsz)

        providers = self._pick_providers()
        self.session = ort.InferenceSession(str(self.model_path), providers=providers)
        self.input_name = self.session.get_inputs()[0].name
        self.provider = self.session.get_providers()[0]
        shape = self.session.get_inputs()[0].shape
        if isinstance(shape[2], int) and shape[2] > 0:
            self.imgsz = int(shape[2])

    @staticmethod
    def _pick_providers() -> List[str]:
        available = ort.get_available_providers()
        preferred = []
        for name in ("CUDAExecutionProvider", "CPUExecutionProvider"):
            if name in available:
                preferred.append(name)
        return preferred or ["CPUExecutionProvider"]

    def detect(self, image_bgr: np.ndarray) -> List[PersonDetection]:
        if image_bgr is None or image_bgr.size == 0:
            return []

        tensor, meta = self._letterbox(image_bgr, self.imgsz)
        outputs = self.session.run(None, {self.input_name: tensor})
        boxes, scores = self._decode(outputs[0], meta)
        if boxes.size == 0:
            return []

        keep = cv2.dnn.NMSBoxes(
            bboxes=boxes.tolist(),
            scores=scores.tolist(),
            score_threshold=self.conf_threshold,
            nms_threshold=self.iou_threshold,
        )
        if keep is None or len(keep) == 0:
            return []

        indices = np.array(keep).reshape(-1)
        found: List[PersonDetection] = []
        for idx in indices:
            x1, y1, x2, y2 = boxes[idx]
            conf = float(scores[idx])
            x1i, y1i, x2i, y2i = int(x1), int(y1), int(x2), int(y2)
            w = max(1, x2i - x1i)
            h = max(1, y2i - y1i)
            box = np.array(
                [[x1i, y1i], [x2i, y1i], [x2i, y2i], [x1i, y2i]],
                dtype=np.float32,
            )
            crop = image_bgr[y1i:y2i, x1i:x2i]
            found.append(
                PersonDetection(
                    type_key=TYPE_PERSON,
                    type_name=TYPE_NAMES[TYPE_PERSON],
                    color_name=_dominant_color_name(crop),
                    confidence=conf,
                    box=box,
                    center=(x1 + w / 2.0, y1 + h / 2.0),
                    angle_deg=90.0 if h >= w else 0.0,
                    length_px=float(max(w, h)),
                    width_px=float(min(w, h)),
                    bbox=(x1i, y1i, w, h),
                )
            )
        return found

    def _letterbox(self, image_bgr: np.ndarray, imgsz: int) -> Tuple[np.ndarray, dict]:
        height, width = image_bgr.shape[:2]
        scale = min(imgsz / height, imgsz / width)
        new_w = int(round(width * scale))
        new_h = int(round(height * scale))
        resized = cv2.resize(image_bgr, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        canvas = np.full((imgsz, imgsz, 3), 114, dtype=np.uint8)
        pad_x = (imgsz - new_w) // 2
        pad_y = (imgsz - new_h) // 2
        canvas[pad_y : pad_y + new_h, pad_x : pad_x + new_w] = resized
        rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        tensor = np.transpose(rgb, (2, 0, 1))[None, ...]
        meta = {
            "scale": scale,
            "pad_x": pad_x,
            "pad_y": pad_y,
            "orig_w": width,
            "orig_h": height,
        }
        return tensor, meta

    def _decode(self, output: np.ndarray, meta: dict) -> Tuple[np.ndarray, np.ndarray]:
        # YOLOv8: (1, 84, 8400) -> (8400, 84)
        preds = np.squeeze(output, axis=0).T
        boxes_xywh = preds[:, :4]
        class_scores = preds[:, 4:]
        person_scores = class_scores[:, PERSON_CLASS_ID]
        mask = person_scores >= self.conf_threshold
        if not np.any(mask):
            return np.zeros((0, 4), dtype=np.float32), np.zeros((0,), dtype=np.float32)

        boxes_xywh = boxes_xywh[mask]
        scores = person_scores[mask]
        boxes = self._xywh_to_xyxy(boxes_xywh)
        boxes = self._unmap(boxes, meta)
        return boxes.astype(np.float32), scores.astype(np.float32)

    @staticmethod
    def _xywh_to_xyxy(boxes: np.ndarray) -> np.ndarray:
        out = np.empty_like(boxes)
        out[:, 0] = boxes[:, 0] - boxes[:, 2] / 2.0
        out[:, 1] = boxes[:, 1] - boxes[:, 3] / 2.0
        out[:, 2] = boxes[:, 0] + boxes[:, 2] / 2.0
        out[:, 3] = boxes[:, 1] + boxes[:, 3] / 2.0
        return out

    @staticmethod
    def _unmap(boxes: np.ndarray, meta: dict) -> np.ndarray:
        scale = meta["scale"]
        pad_x = meta["pad_x"]
        pad_y = meta["pad_y"]
        out = boxes.copy()
        out[:, [0, 2]] = (out[:, [0, 2]] - pad_x) / scale
        out[:, [1, 3]] = (out[:, [1, 3]] - pad_y) / scale
        out[:, [0, 2]] = np.clip(out[:, [0, 2]], 0, meta["orig_w"] - 1)
        out[:, [1, 3]] = np.clip(out[:, [1, 3]], 0, meta["orig_h"] - 1)
        return out


_DETECTOR: Optional[YoloV8PersonDetector] = None


def get_detector(
    model_path: Path | str = DEFAULT_MODEL,
    conf_threshold: float = 0.35,
) -> YoloV8PersonDetector:
    global _DETECTOR
    if _DETECTOR is None:
        _DETECTOR = YoloV8PersonDetector(model_path=model_path, conf_threshold=conf_threshold)
    return _DETECTOR


def detect_people(
    image_bgr: np.ndarray,
    min_confidence: float = 0.35,
    model_path: Path | str = DEFAULT_MODEL,
) -> List[PersonDetection]:
    detector = get_detector(model_path=model_path, conf_threshold=min_confidence)
    if abs(detector.conf_threshold - min_confidence) > 1e-6:
        detector.conf_threshold = min_confidence
    return detector.detect(image_bgr)


def draw_detections(image_bgr: np.ndarray, detections: Sequence[PersonDetection]) -> np.ndarray:
    canvas = image_bgr.copy()
    for det in detections:
        x, y, w, h = det.bbox
        cv2.rectangle(canvas, (x, y), (x + w, y + h), BOX_COLOR, 2, cv2.LINE_AA)

    rgb = cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb)
    draw = ImageDraw.Draw(pil_image)
    font = _font(22)
    for det in detections:
        prefix = f"#{det.track_id} " if det.track_id is not None else ""
        label = f"{prefix}{det.type_name} {det.color_name} {int(det.confidence * 100)}%"
        x, y, _, _ = det.bbox
        x = int(np.clip(x, 0, pil_image.width - 1))
        y = int(np.clip(y - 28, 0, max(pil_image.height - 28, 0)))
        text_box = draw.textbbox((x, y), label, font=font)
        draw.rectangle(text_box, fill=(0, 0, 0))
        draw.text((x, y), label, font=font, fill=(BOX_COLOR[2], BOX_COLOR[1], BOX_COLOR[0]))
    return cv2.cvtColor(np.asarray(pil_image), cv2.COLOR_RGB2BGR)


def _font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except OSError:
        return ImageFont.load_default()


def _dominant_color_name(crop: np.ndarray) -> str:
    if crop is None or crop.size == 0:
        return "未知"
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1].reshape(-1)
    val = hsv[:, :, 2].reshape(-1)
    hue = hsv[:, :, 0].reshape(-1)
    if float(np.median(val)) < 70 or float(np.mean(val < 80)) > 0.55:
        return "深色"
    if float(np.mean(sat > 40)) < 0.25:
        median_v = float(np.median(val))
        if median_v > 185:
            return "浅色"
        return "灰色"
    saturated_hue = hue[sat > 40]
    if saturated_hue.size == 0:
        return "未知"
    peak = int(np.argmax(np.bincount(saturated_hue.astype(np.int32), minlength=180)))
    if peak < 8 or peak >= 170:
        return "红色"
    if peak < 18:
        return "橙色"
    if peak < 38:
        return "黄色"
    if peak < 85:
        return "绿色"
    if peak < 100:
        return "青色"
    if peak < 140:
        return "蓝色"
    return "紫色"
