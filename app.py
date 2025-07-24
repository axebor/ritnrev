import streamlit as st
import os
import zipfile
import tempfile
import base64

# Ikoner inbäddade som base64-strängar (PNG)
pdf_icon_data_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAABXUlEQVR4nO3XsU4DQRAF0RciP4HLRP7/VXfGM2mMDIIgMJAj7JoTPn5rda0okQAAAAAAAAAwNO2HQ9n77hbmH3ncDcY3wNxxfA/HF8D8cXwPxxfA/HF8D8cXwPxxfA/HF8D8cXwPxxdDOzkHj9Wjj9Y+X+mTwvE1xkTqNQAAAAAAAAAAMBqBycwAevQ3a3Ef0qDg3fC8T3n3HLvuFuYfedsz1EdPZ6Vt1Fy6goAAAAAAAAAABg64L8CDOE35ehSGhYAAAAASUVORK5CYII="
zip_icon_data_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAABf0lEQVR4nO2XQQ6DIAxFz+cw/ff7Sk8YpAYnle8UVNP7oKhcS9ZHv5HCFyPhBBCCCGEEEIIIYQQQgghhBBCCCGE0E7o9uwV1Nc/FqpuACWyx4TWv7bBoQD9Evb6LkDzruMe0ogALQLv6B6EDRu8kfdqAwApADz6tV3kHchvmf2G/YvsjGm6Pp6A9gxA9QR8bOUn8KAdx6W2nZAz6A+sInj9oTL78DKMAc5uQA03mQaUAVnwBNnDfl5smZAjgF+4zEDaxRfgmHO4+kLgAoAAAAASUVORK5CYII="

# Appkonfiguration
st.set_page_config(page_title="PDF Comparison", layout="wide")

st.title("🔍 Compare document versions")
st.markdown("Upload two PDF or ZIP files and click **Compare content**.")

col1, col2 = st.columns(2)

with col1:
    file_a = st.file_uploader("📄 Version A", type=["pdf", "zip"], key="file_a")
with col2:
    file_b = st.file_uploader("📄 Version B", type=["pdf", "zip"], key="file_b")


def extract_pdf_names(file):
    if file.name.lower().endswith(".pdf"):
        return [file.name]
    elif file.name.lower().endswith(".zip"):
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(file, "r") as z:
            z.extractall(temp_dir)
        pdfs = [f for f in os.listdir(temp_dir) if f.lower().endswith(".pdf")]
        return sorted(pdfs)
    else:
        return []


def get_icon_for_file(filename):
    if filename.lower().endswith(".pdf"):
        return f'<img src="{pdf_icon_data_url}" width="20"/>'
    elif filename.lower().endswith(".zip"):
        return f'<img src="{zip_icon_data_url}" width="20"/>'
    else:
        return "📄"


if file_a and file_b:
    if st.button("🔍 Compare content"):
        names_a = extract_pdf_names(file_a)
        names_b = extract_pdf_names(file_b)

        st.markdown("### 📋 Comparison result")
        all_files = sorted(set(names_a).union(set(names_b)))

        for name in all_files:
            in_a = name in names_a
            in_b = name in names_b

            icon_html = get_icon_for_file(name)
            col1, col2, col3 = st.columns([5, 1, 1])
            with col1:
                st.markdown(f"{icon_html} {name}", unsafe_allow_html=True)
            with col2:
                st.write("✅" if in_a else "❌")
            with col3:
                st.write("✅" if in_b else "❌")
else:
    st.info("Upload two files to compare.")
