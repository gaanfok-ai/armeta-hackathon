import streamlit as st
import requests
import fitz
import io
import json
import base64
import streamlit.components.v1 as components


API_URL_ANNOTATE = "http://localhost:8000/annotate_pdf"
API_URL_JSON = "http://localhost:8000/predict_json"

st.set_page_config(page_title="YOLO PDF Annotator", layout="wide")

st.title("📄 YOLO PDF Annotator")
st.caption("Detect QR codes, signatures, and stamps in scanned PDFs.")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file:
    st.info(f"**{uploaded_file.name}** — {uploaded_file.size/1024:.1f} KB uploaded")

    # ------- STEP 1: RUN PREDICTIONS --------
    with st.spinner("Running detection..."):
        uploaded_file.seek(0)
        files = {"file": (uploaded_file.name, uploaded_file.read(), "application/pdf")}
        r_json = requests.post(API_URL_JSON, files=files)

    if r_json.status_code != 200:
        st.error("❌ Error from API: " + r_json.text)
        st.stop()

    detections = r_json.json()
    json_str = json.dumps(detections, indent=2, ensure_ascii=False)

    # Detection Summary (Before Preview)

    st.subheader("📋 Detection Summary")

    filename = list(detections.keys())[0]
    pages = detections[filename]

    if not pages:
        st.info("No detections found in this document.")
    else:
        for page_key, page_data in pages.items():
            annos = page_data["annotations"]
            label_counts = {}

            # Count detections by class
            for ann in annos:
                key = list(ann.keys())[0]
                cls = ann[key]["category"]
                label_counts[cls] = label_counts.get(cls, 0) + 1

            # Format readable output
            label_str = ", ".join([f"{k} ({v})" for k, v in label_counts.items()])
            st.write(f"**{page_key}** — {label_str}")


    # annotated pdf generation
    with st.spinner("Generating annotated PDF..."):
        uploaded_file.seek(0)
        files = {"file": (uploaded_file.name, uploaded_file.read(), "application/pdf")}
        r_pdf = requests.post(API_URL_ANNOTATE, files=files)

    if r_pdf.status_code != 200:
        st.error("❌ Error generating PDF: " + r_pdf.text)
        st.stop()

    annotated_pdf_data = r_pdf.content

    st.subheader("📥 Download your results")

    # Two large buttons side-by-side
    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            "📄 Download annotated.pdf",
            data=annotated_pdf_data,
            file_name="annotated.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with col2:
        st.download_button(
            "📥 Download detections.json",
            data=json_str.encode("utf-8"),
            file_name="detections.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("---")

    
    st.subheader("📄 Annotated PDF Preview")

    pdf_stream = io.BytesIO(annotated_pdf_data)
    doc = fitz.open(stream=pdf_stream.read(), filetype="pdf")

    cols = st.columns(2)
    col_idx = 0

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=200)
        img = pix.tobytes("png")

        cols[col_idx].image(img, caption=f"Page {i+1}", use_container_width=True)
        col_idx = (col_idx + 1) % 2

    st.markdown("---")
    st.subheader("🧩 JSON Detection Data")
    st.code(json_str, language="json")


