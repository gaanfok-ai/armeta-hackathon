"""
FastAPI app entrypoint.
Routes:
- POST /annotate_pdf  (multipart form): upload PDF, returns annotated PDF binary
- POST /predict_json  (multipart form): upload PDF, returns JSON detections per page
"""

import io
from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.responses import StreamingResponse
from typing import Optional
from .model_service import ModelService
from .pdf_service import process_pdf_bytes, render_page_to_image, annotate_image_with_detections
from .schemas import PredictResponse, PageDetections, Detection as DetectionSchema
from .utils import configure_logging
import logging
import os

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="YOLO PDF Annotator", version="1.0")

# CONFIG -- path to your best.pt
MODEL_PATH = os.environ.get("YOLO_MODEL_PATH", "models/best.pt")
DEVICE = os.environ.get("YOLO_DEVICE", None)  # e.g. 'cpu' or '0' or 'cuda:0'

# instantiate model service once
try:
    model_service = ModelService(MODEL_PATH, device=DEVICE)
    logger.info("Model loaded.")
except Exception as e:
    logger.exception("Failed to load model at startup. You can still start the server but predictions will fail.")
    model_service = None

@app.post("/annotate_pdf", summary="Upload PDF -> returns annotated PDF")
async def annotate_pdf(file: UploadFile = File(...), dpi: Optional[int] = 150, conf: float = 0.25, iou: float = 0.45):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Upload a PDF file.")
    content = await file.read()
    if model_service is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    logger.info(f"Received PDF ({len(content)} bytes). Running inference...")
    annotated_pdf_bytes = process_pdf_bytes(content, model_service, dpi=dpi, conf=conf, iou=iou)
    return StreamingResponse(io.BytesIO(annotated_pdf_bytes), media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=annotated.pdf"})

@app.post("/predict_json", response_model=PredictResponse, summary="Upload PDF -> return JSON detections per page")
async def predict_json(file: UploadFile = File(...), dpi: Optional[int] = 150, conf: float = 0.25, iou: float = 0.45):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Upload a PDF file.")
    content = await file.read()
    if model_service is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    import fitz
    import numpy as np

    doc = fitz.open(stream=content, filetype="pdf")
    pages_resp = []
    for i in range(doc.page_count):
        page = doc.load_page(i)
        img = render_page_to_image(page, dpi=dpi)
        arr = np.asarray(img)
        dets = model_service.predict(arr, conf=conf, iou=iou)
        det_objs = [DetectionSchema(class_id=d['class_id'], class_name=d['class_name'], conf=d['conf'], bbox=d['bbox']) for d in dets]
        pages_resp.append(PageDetections(page_index=i, detections=det_objs))
    return PredictResponse(pages=pages_resp)

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model_service is not None}
