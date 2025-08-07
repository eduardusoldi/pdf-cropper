import streamlit as st
import fitz  # PyMuPDF
import os
import tempfile

def crop_pdf_to_jpg(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    
    if len(doc) == 0:
        st.error("❌ PDF has no pages.")
        return None

    page = doc[0]
    blocks = page.get_text("blocks")

    if not blocks:
        st.warning("⚠️ No text blocks found.")
        return None

    # Detect bounding box
    x0 = min(b[0] for b in blocks)
    y0 = min(b[1] for b in blocks)
    x1 = max(b[2] for b in blocks)
    y1 = max(b[3] for b in blocks)
    crop_rect = fitz.Rect(x0, y0, x1, y1)

    # Render image
    zoom = 2
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=crop_rect, dpi=300)

    # Save to temp JPG
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    pix.save(temp_file.name)

    return temp_file.name

# === Streamlit UI ===

st.set_page_config(page_title="PDF Resi Cropper", page_icon="📄")
st.title("📄 PDF Resi Cropper to JPG")
st.write("Upload a **single-page PDF**, and this app will crop and convert it to a `.jpg` image based on the content area.")

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    with st.spinner("Processing..."):
        output_path = crop_pdf_to_jpg(uploaded_file)

    if output_path:
        with open(output_path, "rb") as f:
            st.success("✅ Done! Click below to download your cropped JPG.")
            st.download_button("Download Cropped JPG", f, file_name="cropped.jpg", mime="image/jpeg")
        os.unlink(output_path)  # Clean up temp file
