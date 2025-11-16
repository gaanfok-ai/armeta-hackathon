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

@app.post("/predict_json")
async def predict_json(
    file: UploadFile = File(...),
    dpi: Optional[int] = 150,
    conf: float = 0.25,
    iou: float = 0.45
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Upload a PDF file.")

    content = await file.read()
    if model_service is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    import fitz
    import numpy as np

    filename = file.filename
    doc = fitz.open(stream=content, filetype="pdf")

    output = {filename: {}}
    annotation_counter = 1

    for page_index in range(doc.page_count):
        page = doc.load_page(page_index)
        img = render_page_to_image(page, dpi=dpi)
        arr = np.asarray(img)

        detections = model_service.predict(arr, conf=conf, iou=iou)

        # Convert page size
        page_w, page_h = img.size

        # Prepare page dictionary
        page_dict = {
            "annotations": [],
            "page_size": {
                "width": page_w,
                "height": page_h
            }
        }

        for det in detections:
            scale = dpi / 72 
            x0, y0, x1, y1 = det["bbox"]
            pdf_x0 = x0 / scale
            pdf_y0 = y0 / scale
            pdf_w = (x1 - x0) / scale
            pdf_h = (y1 - y0) / scale
            area = pdf_w * pdf_h

            ann_key = f"annotation_{annotation_counter}"
            annotation_counter += 1

            annotation = {
                ann_key: {
                    "category": det["class_name"],
                    "bbox": {
                        "x": float(pdf_x0),
                        "y": float(pdf_y0),
                        "width": float(pdf_w),
                        "height": float(pdf_h)
                    },
                    "area": float(area)
                }
            }

            page_dict["annotations"].append(annotation)

        # Only include pages with annotations
        if len(page_dict["annotations"]) > 0:
            page_key = f"page_{page_index + 1}"
            output[filename][page_key] = page_dict

    return output



@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model_service is not None}
