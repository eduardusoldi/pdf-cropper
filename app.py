import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import tempfile
import numpy as np
import cv2

st.set_page_config(page_title="PDF Cropper", layout="centered")

st.title("🖼️ PDF to Cropped JPG")
st.write("Upload a **Shopee** or **Tokopedia** PDF, and it will auto-crop and convert it to JPG.")

uploaded_file = st.file_uploader("📄 Upload PDF", type="pdf")

def crop_tokopedia_pdf_to_jpg(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    if len(doc) == 0:
        st.error("❌ PDF has no pages.")
        return None

    page = doc[0]

    mat = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=mat, dpi=300)

    # Convert to numpy
    img_np = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 4:
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGBA2RGB)

    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        st.warning("⚠️ No label detected.")
        return None

    # Largest contour is likely the main label
    c = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)

    padding = 10
    x = max(x - padding, 0)
    y = max(y - padding, 0)
    w = min(w + 2 * padding, img_np.shape[1] - x)
    h = min(h + 2 * padding, img_np.shape[0] - y)

    cropped = img_np[y:y + h, x:x + w]
    cropped_pil = Image.fromarray(cropped)

    # Save to file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    temp_file_path = temp_file.name
    temp_file.close()
    cropped_pil.save(temp_file_path)

    return temp_file_path

if uploaded_file is not None:
    with st.spinner("🔄 Processing PDF..."):
        output_path = crop_tokopedia_pdf_to_jpg(uploaded_file)
        if output_path:
            with open(output_path, "rb") as f:
                st.download_button("⬇️ Download Cropped JPG", data=f, file_name="cropped.jpg", mime="image/jpeg")
