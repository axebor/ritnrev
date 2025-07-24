import streamlit as st
import os
import zipfile
import tempfile

st.set_page_config(page_title="PDF-jämförelse", layout="wide")

st.title("🔍 Jämför två versioner av handlingar")
st.markdown("Ladda upp två PDF- eller ZIP-filer och klicka på **Jämför**.")

col1, col2 = st.columns(2)

with col1:
    file_a = st.file_uploader("📁 Version A", type=["pdf", "zip"], key="file_a")
with col2:
    file_b = st.file_uploader("📁 Version B", type=["pdf", "zip"], key="file_b")

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

def file_icon(filename):
    return "📄" if filename.lower().endswith(".pdf") else "🗜️"

if file_a and file_b:
    if st.button("🔍 Jämför"):
        names_a = extract_pdf_names(file_a)
        names_b = extract_pdf_names(file_b)

        st.markdown("### 📋 Jämförelseresultat")

        all_files = sorted(set(names_a).union(set(names_b)))

        for name in all_files:
            in_a = name in names_a
            in_b = name in names_b

            col1, col2, col3 = st.columns([5, 1, 1])
            with col1:
                st.write(f"{file_icon(name)} {name}")
            with col2:
                st.write("✅" if in_a else "❌")
            with col3:
                st.write("✅" if in_b else "❌")
else:
    st.info("Ladda upp två filer för att kunna jämföra.")
