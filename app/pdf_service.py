"""
PDF processing utilities:
- render PDF pages to images (PIL)
- run model on each page
- draw boxes on pages and reassemble into a single annotated PDF (raster)
"""

from typing import List, Tuple, Dict, Any
import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import io
import numpy as np
import logging

logger = logging.getLogger(__name__)

# default render DPI scale (higher = better detection, slower)
DEFAULT_DPI = 500 # 150 dpi is a good balance for scanned docs

def render_page_to_image(page: fitz.Page, dpi: int = DEFAULT_DPI) -> Image.Image:
    """
    Render a PyMuPDF page to a PIL Image at target dpi.
    """
    # scale factor: 72 points per inch is PDF default. scale = dpi/72
    scale = dpi / 72
    mat = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return img

def annotate_image_with_detections(img: Image.Image, detections: List[Dict[str, Any]], box_thickness: int = 3) -> Image.Image:
    """
    Draw bounding boxes and labels onto a copy of the input image.
    detections: list with 'bbox' in pixel coordinates relative to the image.
    """
    draw = ImageDraw.Draw(img)
    try:
        # Use a default truetype font if available
        font = ImageFont.load_default()
    except Exception:
        font = None

    for det in detections:
        x0, y0, x1, y1 = det["bbox"]
        # draw rectangle
        for t in range(box_thickness):
            draw.rectangle([x0 - t, y0 - t, x1 + t, y1 + t], outline="red")
        # label
        label = f"{det['class_name']} {det['conf']:.2f}"
        # Compute text bounding box
        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Background rectangle behind text
        text_bg = [x0, y0 - text_h - 4, x0 + text_w + 4, y0]
        draw.rectangle(text_bg, fill="red")

        # Draw label text
        draw.text((x0 + 2, y0 - text_h - 2), label, fill="white", font=font)

    return img

def process_pdf_bytes(pdf_bytes: bytes, model_service, dpi: int = DEFAULT_DPI, conf: float = 0.25, iou: float = 0.45) -> bytes:
    """
    Takes PDF bytes, runs detection on each page, draws boxes, returns annotated PDF bytes.
    model_service: instance with .predict(np_image, conf, iou)
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    annotated_images = []

    for i in range(doc.page_count):
        page = doc.load_page(i)
        img = render_page_to_image(page, dpi=dpi)
        # convert to numpy (ultralytics accepts numpy HWC RGB)
        arr = np.asarray(img)  # RGB
        # run model
        detections = model_service.predict(arr, conf=conf, iou=iou)
        # annotate
        annotated_img = img.copy()
        annotated_img = annotate_image_with_detections(annotated_img, detections)
        annotated_images.append(annotated_img.convert("RGB"))

    # Save images to a single multi-page PDF in memory
    output = io.BytesIO()
    if not annotated_images:
        # If no pages, return original PDF
        return pdf_bytes
    annotated_images[0].save(output, format="PDF", save_all=True, append_images=annotated_images[1:])
    output.seek(0)
    return output.read()
