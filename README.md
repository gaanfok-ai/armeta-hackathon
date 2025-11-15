YOLO PDF Annotator

Detect QR codes, signatures, and stamps on scanned documents using YOLOv8 and annotate PDFs automatically.
Includes:

FastAPI backend (model inference + PDF annotation)

Streamlit frontend (upload, preview, magnifier, download)

Custom JSON output format

Loupe-style hover magnifier for PDF pages

⚙️ Installation
1) Clone the repo
git clone <your-repo-url>
cd <your-project-folder>

2) Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

Windows:

venv\Scripts\activate

Linux:
source venv/bin/activate

3) Install dependencies
pip install -r requirements.txt

🚀 Running the Application

Your system has two processes:

FastAPI backend (API + model inference)

Streamlit frontend (UI)

1️⃣ Start FastAPI backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


Backend will start at:

http://localhost:8000


Interactive API docs (Swagger):

http://localhost:8000/docs

2️⃣ Start Streamlit UI
streamlit run ui/ui_app.py


UI will be available at:

http://localhost:8501

🔌 API Endpoints
POST /predict_json

Upload PDF → returns custom JSON format with detections.

POST /annotate_pdf

Upload PDF → returns annotated PDF as bytes.

GET /health

Simple health check.

🧩 Example JSON Response Format
{
  "document.pdf": {
    "page_1": {
      "annotations": [
        {
          "annotation_117": {
            "category": "signature",
            "bbox": {
              "x": 510,
              "y": 146,
              "width": 250,
              "height": 98.89
            },
            "area": 24722.5
          }
        }
      ],
      "page_size": {
        "width": 1684,
        "height": 1190
      }
    }
  }
}