import streamlit as st
import os
import zipfile
import tempfile
import pdfplumber
from difflib import SequenceMatcher
from pdf2image import convert_from_path
from PIL import ImageChops, Image

st.set_page_config(page_title="PDF-jämförelse", layout="wide")

st.title("🔍 Jämför två versioner av handlingar")
st.markdown("Ladda upp två PDF- eller ZIP-filer och klicka på **Jämför**.")

col1, col2 = st.columns(2)
with col1:
    file_a = st.file_uploader("📁 Version A", type=["pdf", "zip"], key="file_a")
with col2:
    file_b = st.file_uploader("📁 Version B", type=["pdf", "zip"], key="file_b")

def extract_pdfs(file):
    result = {}
    if file.name.lower().endswith(".pdf"):
        temp_dir = tempfile.mkdtemp()
        path = os.path.join(temp_dir, file.name)
        with open(path, "wb") as f:
            f.write(file.read())
        result[file.name] = path
    elif file.name.lower().endswith(".zip"):
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(file, "r") as z:
            z.extractall(temp_dir)
        for root, _, files in os.walk(temp_dir):
            for f in files:
                if f.lower().endswith(".pdf"):
                    rel_path = os.path.relpath(os.path.join(root, f), temp_dir)
                    result[rel_path.replace("\\", "/")] = os.path.join(root, f)
    return result

def extract_text(path):
    try:
        with pdfplumber.open(path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except:
        return ""

def compare_text(path_a, path_b, threshold=0.98):
    text_a = extract_text(path_a)
    text_b = extract_text(path_b)
    ratio = SequenceMatcher(None, text_a, text_b).ratio()
    return ratio < threshold

def compare_images(path_a, path_b):
    try:
        images_a = convert_from_path(path_a, first_page=1, last_page=1, dpi=100)
        images_b = convert_from_path(path_b, first_page=1, last_page=1, dpi=100)

        img_a = images_a[0].convert("RGB")
        img_b = images_b[0].convert("RGB")

        diff = ImageChops.difference(img_a, img_b)
        bbox = diff.getbbox()

        return bbox is not None  # True om bild skiljer sig
    except:
        return False

def file_icon(filename):
    return "📄" if filename.lower().endswith(".pdf") else "🗜️"

if file_a and file_b:
    if st.button("🔍 Jämför"):
        pdfs_a = extract_pdfs(file_a)
        pdfs_b = extract_pdfs(file_b)

        names_a = set(pdfs_a.keys())
        names_b = set(pdfs_b.keys())
        all_files = sorted(names_a.union(names_b))

        st.markdown("### 📋 Jämförelsetabell")

        header = st.columns([4, 2, 2, 2, 3])
        header[0].markdown("**Filnamn**")
        header[1].markdown("**I Version A**")
        header[2].markdown("**I Version B**")
        header[3].markdown("**Skillnad i innehåll**")
        header[4].markdown("**Typ av skillnad**")

        for name in all_files:
            in_a = name in pdfs_a
            in_b = name in pdfs_b
            row = st.columns([4, 2, 2, 2, 3])

            with row[0]:
                st.write(f"{file_icon(name)} {name}")
            with row[1]:
                st.write("✅ Ja" if in_a else "❌ Nej")
            with row[2]:
                st.write("✅ Ja" if in_b else "❌ Nej")

            if in_a and in_b:
                text_changed = compare_text(pdfs_a[name], pdfs_b[name])
                if text_changed:
                    with row[3]: st.write("⚠️")
                    with row[4]: st.write("Text ändrad")
                else:
                    image_changed = compare_images(pdfs_a[name], pdfs_b[name])
                    with row[3]: st.write("⚠️" if image_changed else "–")
                    with row[4]: st.write("Bild/ritning ändrad" if image_changed else "–")
            else:
                with row[3]:
                    st.write("–")
                with row[4]:
                    st.write("Saknas i B" if in_a and not in_b else "Saknas i A" if in_b and not in_a else "–")
else:
    st.info("Ladda upp två filer för att kunna jämföra.")
