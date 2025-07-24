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
        pdfs = []
        for root, _, files in os.walk(temp_dir):
            for f in files:
                if f.lower().endswith(".pdf"):
                    rel_path = os.path.relpath(os.path.join(root, f), temp_dir)
                    pdfs.append(rel_path.replace("\\", "/"))
        return sorted(pdfs)
    else:
        return []

def file_icon(filename):
    return "📄" if filename.lower().endswith(".pdf") else "🗜️"

if file_a and file_b:
    if st.button("🔍 Jämför"):
        names_a = extract_pdf_names(file_a)
        names_b = extract_pdf_names(file_b)

        st.markdown("### 📋 Jämförelsetabell")

        all_files = sorted(set(names_a).union(set(names_b)))

        header_cols = st.columns([5, 2, 2])
        with header_cols[0]:
            st.markdown("**Filnamn**")
        with header_cols[1]:
            st.markdown("**Finns i Version A**")
        with header_cols[2]:
            st.markdown("**Finns i Version B**")

        for name in all_files:
            in_a = name in names_a
            in_b = name in names_b

            row = st.columns([5, 2, 2])
            with row[0]:
                st.write(f"{file_icon(name)} {name}")
            with row[1]:
                st.write("✅ Ja" if in_a else "❌ Nej")
            with row[2]:
                st.write("✅ Ja" if in_b else "❌ Nej")
else:
    st.info("Ladda upp två filer för att kunna jämföra.")
