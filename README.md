<div align="center">

# **Document Scan Annotator**
Detects **QR codes**, **signatures**, and **different stamps** on scanned PDFs using fine-tuned **YOLOv12m** on a custom dataset, with a **FastAPI backend** and a **Streamlit frontend**.

---

### *PDF → Detection → Annotated PDF & JSON → Interactive UI*
Modern, clean, and production-ready.

</div>

---

# 📚 **Table of Contents**
- [ Model](#-model)
- [📦 Features](#-features)
- [⚙️ Installation](#️-installation)
- [🚀 Running the Application](#-running-the-application)
- [🔌 API Endpoints](#-api-endpoints)
- [🧩 Example JSON Response](#-example-json-response)
- [🖼️ Streamlit UI Features](#️-streamlit-ui-features)

---
# 🧠 **Model & Dataset Information**

This repository uses a **fine-tuned YOLOv12m model** designed to detect on the scanned documents/papers:

- Signatures  
- Stamps(it classifies it in differnt shapes: 'stamp_circle', 'stamp_oval', 'stamp_rect', 'stamp_triangle', 'stamp_wax', 'stamp_word')
- QR and bar codes
- Fingerprints

The model and dataset documentation are kept in a dedicated folder to avoid cluttering the main project and because the dataset may be too large to store directly in the repository.
**For detailed information please refer to `model/README.md`

---

# 📦 **Features**
- Upload scanned PDF documents  
- Detect:
  - ✒️ Signatures  
  - 📮 Stamps of different types  
  - 📎 QR Codes
  - Bar codes
  - Fingerprints
- Generate:
  - ✔ Annotated PDF with bounding boxes  
  - ✔ JSON output in a **custom format**  
- Interactive UI:
  - 🔍 Hover magnifier (loupe)  
  - 📄 Annotated preview  
  - 📥 One-click downloads  
- Removes pages with no detections in JSON  
- Clean, responsive interface
- Accurate multi-class detection


---

# ⚙️ **Installation**

> 📌 *Tested on Python 3.9–3.12.*

### **1) Clone the repository**

```bash
$ git clone <your-repo-url>
$ cd <your-project-folder>
```
**2) Create a virtual environment**
```bash
$ python3 -m venv venv
$ source venv/bin/activate
```
** windows: **
```bash
$ venv\Scripts\activate
```
** Linux: **
```bash
$ venv\Scripts\activate
```
### **3) Install dependencies**

```bash
(venv) $ pip install -r requirements.txt
```

--- 

# 🚀 **Running the Application**

The application runs two separate services:

✔ *FastAPI backend*
✔ *Streamlit frontend*

### 1️⃣Start the FastAPI backend
```bash
(venv) $ uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend available at:
http://localhost:8000

Swagger docs:
http://localhost:8000/docs

###  2️⃣Start the Streamlit UI
```bash
(venv) $ streamlit run ui/ui_app.py
```
UI available at:
http://localhost:8501

---

# 🔌 API Endpoints

*POST /predict_json*

Upload PDF → returns detection JSON.

*POST /annotate_pdf*

Upload PDF → returns annotated PDF file.

*GET /health*

Simple health check.

---

# 🧩 Example JSON Response
```json
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
```

--- 

# 🖼️ Streamlit UI Features

📄 PDF uploader

⚡ Automatic inference on backend

👁 Annotated page previews

🔍 Hover magnifier tool (loupe)

📥 Download:
  - annotated PDF
  - JSON results

🧩 JSON viewer with syntax highlighting

Responsive layout (2-column preview)

---
# Load Testing
To test system for different loads you may use locustfile

```bash
locust -f locustfile.py
```
Then go to: http://localhost:8089 and test with different configurations