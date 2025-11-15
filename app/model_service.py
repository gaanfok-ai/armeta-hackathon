"""
Model loading and inference wrapper.
Provides a simple interface to run the ultralytics YOLO model on PIL/np images.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from ultralytics import YOLO
import logging

logger = logging.getLogger(__name__)

class ModelService:
    def __init__(self, model_path: str, device: Optional[str] = None):
        """
        model_path: path to best.pt
        device: 'cpu' or '0' or 'cuda:0'. If None, YOLO chooses default.
        """
        self.model_path = model_path
        logger.info(f"Loading YOLO model from {model_path} (device={device})")
        # device argument passed to YOLO() or to .predict
        self.model = YOLO(model_path)
        self.device = device

    def predict(self, img: np.ndarray, conf: float = 0.25, iou: float = 0.45) -> List[Dict[str, Any]]:
        """
        img: HxWxC uint8 numpy array (BGR or RGB both accepted; ultralytics handles numpy arrays)
        Returns: list of detections: each dict: {class_id, class_name, conf, bbox: [x0,y0,x1,y1]}
        Coordinates are in pixel space relative to the provided img.
        """
        # ultralytics returns Results objects; using model.predict to control args
        results = self.model.predict(
        source=img,
        conf=conf,
        iou=iou,
        device=self.device,
        verbose=False)
        # Usually results is a list, one per image - we passed single image
        if not results:
            return []
        res = results[0]
        dets = []
        boxes = res.boxes  # ultralytics Boxes object
        names = self.model.model.names if hasattr(self.model, "model") and hasattr(self.model.model, "names") else {}
        for box in boxes:
            xyxy = box.xyxy.cpu().numpy().tolist()[0]  # shape (1,4) -> [x1,y1,x2,y2]
            conf_score = float(box.conf.cpu().numpy().tolist()[0])
            cls_id = int(box.cls.cpu().numpy().tolist()[0])
            dets.append({
                "class_id": cls_id,
                "class_name": names.get(cls_id, str(cls_id)),
                "conf": conf_score,
                "bbox": [float(xyxy[0]), float(xyxy[1]), float(xyxy[2]), float(xyxy[3])]
            })
        return dets
