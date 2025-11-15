from pydantic import BaseModel
from typing import List

class Detection(BaseModel):
    class_id: int
    class_name: str
    conf: float
    bbox: List[float]  # [x0,y0,x1,y1]

class PageDetections(BaseModel):
    page_index: int
    detections: List[Detection]

class PredictResponse(BaseModel):
    pages: List[PageDetections]
