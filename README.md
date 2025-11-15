📄 README.md
Document Object Detector

Detect QR codes, signatures, and stamps from uploaded PDFs or images using a locally deployed YOLOv12-based inference API and a simple web interface.

This project supports:

✓ Multi-page PDF input

✓ YOLOv12 detection for: signature, stamp, qr

✓ PDF → Image conversion

✓ JSON annotation output

✓ Annotated preview images

✓ A local FastAPI backend

✓ A simple front-end UI

✓ Standalone inference scripts (for debugging)

🚀 Features
Component	Description
YOLOv12 Model	Custom-trained model for document elements
FastAPI Backend	Upload PDFs/images + return detections
Local UI	Simple HTML upload page
PDF Support	Converts PDFs to high-resolution images
QR Reading	Using YOLO (detection), optionally OpenCV for decoding
Standalone Scripts	Test inference without API
📦 Installation
1. Clone the repository
git clone <your_repo_url>
cd project/

2. Create environment
conda create -n yolo python=3.10 -y
conda activate yolo

3. Install dependencies
pip install ultralytics pdf2image fastapi uvicorn pillow opencv-python


⚠ Linux only:
If using pyzbar (not required now):

sudo apt-get install libzbar0


But the project uses OpenCV QRCodeDetector, so this step is optional.

📁 Project Structure
project/
│
├── main.py                  # FastAPI server
├── ui/
│   └── index.html           # Simple upload UI
├── detectors/
│   ├── yolo_detector.py     # YOLO inference logic
│   ├── qr_reader.py         # Optional OpenCV QR decoder
│   └── pdf_utils.py         # PDF → image conversion
│
├── runs/                    # YOLO inference output
├── models/
│   └── best.pt              # Your trained YOLOv12 model
│
├── local_test.py            # Standalone test script
└── README.md

🧠 Model Training
Simple training:
from ultralytics import YOLO
model = YOLO("yolo12m.pt")
model.train(
    data="dataset.yaml",
    epochs=30,
    imgsz=768,
    batch=8
)

Transfer learning using your weights:
model = YOLO("yolo12m.pt")  # COCO pretrained
model.train(
    data="dataset.yaml",
    epochs=30,
    imgsz=768,
    pretrained=True
)


Best starting weights for documents:

yolo12m.pt


because:

Good trade-off accuracy/speed

Faster training

Learns small objects (signatures, QR)

🔍 Standalone Local Inference (Debug Mode)

This verifies the model without FastAPI.

Create local_test.py:

from ultralytics import YOLO

model = YOLO("models/best.pt")

results = model.predict(
    source="test.jpg",
    imgsz=768,
    conf=0.25,
    save=True
)

print("Saved to:", results[0].save_dir)


Run:

python local_test.py


Output saved to:

runs/detect/predict/


Compare this with what the web UI outputs.

⚙ Running the FastAPI Server

Start server:

uvicorn main:app --host 0.0.0.0 --port 8000 --reload


Visit:

Swagger UI:
👉 http://127.0.0.1:8000/docs

Front-end UI:
👉 http://127.0.0.1:8000

🖥 Using the Web UI

The web UI supports PDF or image uploads.

Open browser

Go to http://127.0.0.1:8000

Upload a PDF or JPG

Get JSON results + annotated preview

📄 PDF Processing

This project uses:

from pdf2image import convert_from_path

pages = convert_from_path(pdf_file, dpi=300)


All pages become PIL images → then YOLO model runs inference on each page.

🔎 Detection Output Format

Example output:

{
  "page_1": {
    "page_size": { "width": 1684, "height": 1190 },
    "annotations": [
      {
        "annotation_0": {
          "category": "stamp",
          "bbox": { "x": 520, "y": 842, "width": 223, "height": 227 }
        }
      }
    ]
  }
}


This matches your original annotation format.

🧰 Troubleshooting
❗ Error: “Unable to find zbar shared library”

Solution: use OpenCV QR reader (already configured).
No system dependency needed.

❗ Error: Address already in use

Kill the previous server:

sudo lsof -t -i:8000 | xargs kill -9

❗ Web output differs from local output

Check:

resolution (DPI)

preprocessing

confidence threshold

wrong weights loaded

input resizing

Use local_test.py to compare outputs directly.
# armeta-hackathon
