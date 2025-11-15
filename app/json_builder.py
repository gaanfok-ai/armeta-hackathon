import uuid
from typing import Dict, List


def generate_annotation_id() -> str:
    """Generate a unique annotation ID."""
    return f"annotation_{uuid.uuid4().int % 10000}"


def xyxy_to_xywh(x1, y1, x2, y2):
    """Convert YOLO xyxy to x,y,width,height format."""
    return {
        "x": float(x1),
        "y": float(y1),
        "width": float(x2 - x1),
        "height": float(y2 - y1),
    }


def build_page_annotation_dict(
    detections: List[Dict],
    page_width: int,
    page_height: int,
) -> Dict:
    """
    Build structured annotation dictionary for a single page.
    """

    page_dict = {
        "annotations": [],
        "page_size": {"width": page_width, "height": page_height},
    }

    for det in detections:
        ann_id = generate_annotation_id()
        category = det["class"]
        bbox_xyxy = det["bbox"]  # [x1, y1, x2, y2]

        # Convert to final format
        bbox_xywh = xyxy_to_xywh(*bbox_xyxy)

        area = bbox_xywh["width"] * bbox_xywh["height"]

        page_dict["annotations"].append({
            ann_id: {
                "category": category,
                "bbox": bbox_xywh,
                "area": float(area)
            }
        })

    return page_dict


def insert_into_document_structure(
    doc_json: Dict,
    filename: str,
    page_number: int,
    page_data: Dict,
):
    """Insert structured page annotations into full document JSON."""

    if filename not in doc_json:
        doc_json[filename] = {}

    page_key = f"page_{page_number}"
    doc_json[filename][page_key] = page_data

    return doc_json
