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

        set_a = set(names_a)
        set_b = set(names_b)

        both = sorted(set_a & set_b)
        only_a = sorted(set_a - set_b)
        only_b = sorted(set_b - set_a)

        st.markdown("### ✅ Filer som finns i **båda versionerna**")
        if both:
            for name in both:
                st.write(f"{file_icon(name)} {name}")
        else:
            st.write("_Inga gemensamma filer_")

        st.markdown("---")
        st.markdown("### ❌ Filer som finns **endast i Version A**")
        if only_a:
            for name in only_a:
                st.write(f"{file_icon(name)} {name}")
        else:
            st.write("_Inga unika filer i Version A_")

        st.markdown("---")
        st.markdown("### ❌ Filer som finns **endast i Version B**")
        if only_b:
            for name in only_b:
                st.write(f"{file_icon(name)} {name}")
        else:
            st.write("_Inga unika filer i Version B_")
else:
    st.info("Ladda upp två filer för att kunna jämföra.")
