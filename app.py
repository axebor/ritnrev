import streamlit as st
import os
import zipfile
import tempfile
import pdfplumber
from difflib import SequenceMatcher
from PIL import ImageChops, Image
import fitz  # PyMuPDF
import time
import io

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
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, temp_dir)
                    result[rel_path.replace("\\", "/").split("/")[-1]] = full_path
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

def compare_images(path_a, path_b, progress_callback=None):
    name = os.path.basename(path_a)
    try:
        doc_a = fitz.open(path_a)
        doc_b = fitz.open(path_b)

        num_pages = min(len(doc_a), len(doc_b))
        total_score = 0

        for i in range(num_pages):
            if progress_callback:
                progress_callback((i + 1) / num_pages)
            time.sleep(0.1)

            pix_a = doc_a[i].get_pixmap(dpi=300)
            pix_b = doc_b[i].get_pixmap(dpi=300)

            img_a = Image.open(io.BytesIO(pix_a.tobytes("png"))).convert("RGB")
            img_b = Image.open(io.BytesIO(pix_b.tobytes("png"))).convert("RGB")

            if img_a.size != img_b.size:
                return True, i + 1, total_score

            diff = ImageChops.difference(img_a, img_b)
            diff_score = sum(sum(pixel) for pixel in diff.getdata())
            total_score += diff_score

            if diff_score > 1:
                return True, i + 1, total_score

        return False, None, total_score

    except Exception as e:
        print(f"[{name}] Bildjämförelse fel:", e)
        return False, None, 0

def file_icon(filename):
    return "📄" if filename.lower().endswith(".pdf") else "🧼"

if file_a and file_b:
    if st.button("🔍 Jämför"):
        st.markdown("🚀 **Analys startar – scrolla ner för resultat...**")
        total_progress_bar = st.progress(0.0)

        pdfs_a = extract_pdfs(file_a)
        pdfs_b = extract_pdfs(file_b)
        all_names = sorted(set(pdfs_a.keys()).union(set(pdfs_b.keys())))

        st.markdown("### 📋 Jämförelsetabell")
        header = st.columns([4, 2, 2, 2, 3])
        header[0].markdown("**Filnamn**")
        header[1].markdown("**I Version A**")
        header[2].markdown("**I Version B**")
        header[3].markdown("**Skillnad i innehåll**")
        header[4].markdown("**Typ av skillnad**")

        total_files = len(all_names)
        for idx, name in enumerate(all_names):
            in_a = name in pdfs_a
            in_b = name in pdfs_b
            row = st.columns([4, 2, 2, 2, 3])

            with row[0]: st.write(f"{file_icon(name)} {name}")
            with row[1]: st.write("✅ Ja" if in_a else "❌ Nej")
            with row[2]: st.write("✅ Ja" if in_b else "❌ Nej")

            progress_placeholder = row[3].empty()
            type_placeholder = row[4].empty()

            if in_a and in_b:
                path_a = pdfs_a[name]
                path_b = pdfs_b[name]

                text_changed = compare_text(path_a, path_b)
                if text_changed:
                    progress_placeholder.write("⚠️")
                    type_placeholder.write("Text ändrad")
                else:
                    progress_bar = progress_placeholder.progress(0.0)

                    def update_progress(value):
                        progress_bar.progress(value)

                    img_changed, page, score = compare_images(path_a, path_b, progress_callback=update_progress)
                    progress_bar.empty()

                    if score > 0:
                        progress_placeholder.write(f"Diff-score: {score}")
                    if img_changed:
                        type_placeholder.write(f"Bild ändrad (sida {page})")
                    else:
                        type_placeholder.write("–")
            else:
                progress_placeholder.write("–")
                type_placeholder.write("Saknas i B" if in_a and not in_b else "Saknas i A" if in_b and not in_a else "–")

            total_progress_bar.progress((idx + 1) / total_files)
else:
    st.info("Ladda upp två filer för att kunna jämföra.")
