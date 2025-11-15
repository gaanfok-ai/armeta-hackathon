<div align="center">

# **YOLO PDF Annotator**
Detect **QR codes**, **signatures**, and **stamps** on scanned PDFs using **YOLOv8**, with a **FastAPI backend** and a **Streamlit frontend**.

---

### 🚀 *PDF → Detection JSON → Annotated PDF → Interactive UI*
Modern, clean, and production-ready.

</div>

---

# 📚 **Table of Contents**
- [📦 Features](#-features)
- [⚙️ Installation](#️-installation)
- [🚀 Running the Application](#-running-the-application)
- [🔌 API Endpoints](#-api-endpoints)
- [🧩 Example JSON Response](#-example-json-response)
- [🖼️ Streamlit UI Features](#️-streamlit-ui-features)
- [🛠️ Troubleshooting](#-troubleshooting)
- [🏁 Deployment Notes](#-deployment-notes)

---

# 📦 **Features**
- Upload scanned PDF documents  
- Detect:
  - ✒️ Signatures  
  - 📮 Stamps  
  - 📎 QR Codes  
- Generate:
  - ✔ Annotated PDF with bounding boxes  
  - ✔ JSON output in a **custom format**  
- Interactive UI:
  - 🔍 Hover magnifier (loupe)  
  - 📄 Annotated preview  
  - 📥 One-click downloads  
- Removes pages with no detections  
- Clean, responsive interface  

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


#🔌 API Endpoints

*POST /predict_json*

Upload PDF → returns detection JSON.

*POST /annotate_pdf*

Upload PDF → returns annotated PDF file.

*GET /health*

Simple health check.
