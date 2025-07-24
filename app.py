import os
import zipfile
import tempfile
import streamlit as st

st.set_page_config(page_title="Bygghandlingsjämförelse", layout="wide")
st.title("📁 Jämför två versioner av bygghandlingar")
st.markdown("Ladda upp två zip-filer med PDF:er. Systemet kommer att matcha filnamn och visa status per fil.")

col1, col2 = st.columns(2)
with col1:
    zip_a = st.file_uploader("🔹 Version A (t.ex. PRD)", type="zip", key="zip_a")
with col2:
    zip_b = st.file_uploader("🔸 Version B (t.ex. bygghandling)", type="zip", key="zip_b")

def extract_zip_to_temp(zip_file):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_file, "r") as z:
        z.extractall(temp_dir)
    return temp_dir

def list_pdfs_in_folder(folder):
    return sorted([
        f for f in os.listdir(folder)
        if f.lower().endswith(".pdf")
    ])

if zip_a and zip_b:
    st.markdown("### 📂 Matchade filer")

    dir_a = extract_zip_to_temp(zip_a)
    dir_b = extract_zip_to_temp(zip_b)

    pdfs_a = set(list_pdfs_in_folder(dir_a))
    pdfs_b = set(list_pdfs_in_folder(dir_b))

    all_files = sorted(pdfs_a.union(pdfs_b))

    st.write("**Status:** ✅ = finns | ❌ = saknas")
    st.markdown("---")

    for filename in all_files:
        in_a = filename in pdfs_a
        in_b = filename in pdfs_b

        col1, col2, col3 = st.columns([4, 2, 2])
        with col1:
            st.write(f"📄 {filename}")
        with col2:
            st.write("✅ Ja" if in_a else "❌ Nej")
        with col3:
            st.write("✅ Ja" if in_b else "❌ Nej")
else:
    st.info("Ladda upp två zip-filer med PDF:er för att fortsätta.")
