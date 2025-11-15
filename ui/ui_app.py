import streamlit as st
import requests
import fitz  # PyMuPDF
import io

# ---- CONFIG ----
API_URL_ANNOTATE = "http://localhost:8000/annotate_pdf"
API_URL_JSON = "http://localhost:8000/predict_json"

st.set_page_config(page_title="YOLO PDF Annotator", layout="wide")

st.title("📄 YOLO PDF Annotator")
st.caption("Upload a scanned document containing QR / stamp / signature. Get annotated PDF and detection results.")

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:
    # Show upload info
    st.info(f"File: **{uploaded_file.name}** ({uploaded_file.size/1024:.1f} KB)")

    with st.spinner("Running detection..."):
        # Send JSON request
        files = {"file": (uploaded_file.name, uploaded_file.read(), "application/pdf")}
        res_json = requests.post(API_URL_JSON, files=files)

        if res_json.status_code != 200:
            st.error("Error from API: " + res_json.text)
            st.stop()

        detections = res_json.json()

    # Display detections
    st.subheader("🔍 Detection Results")
    st.json(detections)

    # Re-upload file content for annotation request
    uploaded_file.seek(0)
    files = {"file": (uploaded_file.name, uploaded_file.read(), "application/pdf")}

    with st.spinner("Generating annotated PDF..."):
        res_pdf = requests.post(API_URL_ANNOTATE, files=files)

        if res_pdf.status_code != 200:
            st.error("Error generating annotated PDF: " + res_pdf.text)
            st.stop()

        annotated_pdf_data = res_pdf.content

    # Download button
    st.subheader("📥 Download Annotated PDF")
    st.download_button(
        label="Download annotated.pdf",
        data=annotated_pdf_data,
        file_name="annotated.pdf",
        mime="application/pdf"
    )

    # Render preview
    st.subheader("📄 Preview")
    pdf_stream = io.BytesIO(annotated_pdf_data)
    doc = fitz.open(stream=pdf_stream.read(), filetype="pdf")

    num_cols = 2
    col_index = 0
    cols = st.columns(num_cols)

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=110)
        img_bytes = pix.tobytes("png")

        cols[col_index].image(img_bytes, caption=f"Page {i+1}")
        col_index = (col_index + 1) % num_cols
