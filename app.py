import streamlit as st
import os
import zipfile
import tempfile
import base64

st.set_page_config(page_title="PDF-jämförelse", layout="wide")

# === Ikoner (uppdatera sökvägar här) ===
def get_icon_data_url(path):
    with open(path, "rb") as f:
        return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"

pdf_icon = get_icon_data_url("/mnt/data/23399bc7-ab5d-47e3-b02a-0e670e12e516.png")
zip_icon = get_icon_data_url("/mnt/data/Icons8-Windows-8-Files-Zip.512.png")  # Denna fil laddade du upp tidigare

# === Layout ===
st.title("🔍 Jämför två versioner av handlingar")
st.markdown("Ladda upp två PDF- eller ZIP-filer och klicka på **Jämför**.")

col1, col2 = st.columns(2)
with col1:
    file_a = st.file_uploader("📄 Version A", type=["pdf", "zip"], key="file_a")
with col2:
    file_b = st.file_uploader("📄 Version B", type=["pdf", "zip"], key="file_b")

# === Extrahera PDF-namn från fil ===
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

# === Jämförelsefunktion ===
if file_a and file_b:
    if st.button("🔍 Jämför"):
        names_a = extract_pdf_names(file_a)
        names_b = extract_pdf_names(file_b)
        all_files = sorted(set(names_a).union(set(names_b)))

        st.markdown("### 📋 Jämförelseresultat")
        for name in all_files:
            in_a = name in names_a
            in_b = name in names_b
            icon = pdf_icon if name.lower().endswith(".pdf") else zip_icon

            col1, col2, col3 = st.columns([5, 1, 1])
            with col1:
                st.markdown(f'<img src="{icon}" width="20" style="vertical-align:middle; margin-right:8px;"> {name}', unsafe_allow_html=True)
            with col2:
                st.write("✅" if in_a else "❌")
            with col3:
                st.write("✅" if in_b else "❌")
else:
    st.info("Ladda upp två filer för att kunna jämföra.")
