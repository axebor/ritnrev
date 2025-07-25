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

def compare_images(path_a, path_b, progress_callback=None, total_pages_done=0, total_pages=1):
    name = os.path.basename(path_a)
    try:
        doc_a = fitz.open(path_a)
        doc_b = fitz.open(path_b)
        num_pages = min(len(doc_a), len(doc_b))

        for i in range(num_pages):
            pix_a = doc_a[i].get_pixmap(dpi=150)
            pix_b = doc_b[i].get_pixmap(dpi=150)

            img_a = Image.open(io.BytesIO(pix_a.tobytes("png"))).convert("RGB")
            img_b = Image.open(io.BytesIO(pix_b.tobytes("png"))).convert("RGB")

            if img_a.size != img_b.size:
                if progress_callback:
                    progress_callback((total_pages_done + i + 1) / total_pages)
                return True, i + 1

            diff = ImageChops.difference(img_a, img_b)
            diff_score = sum(sum(pixel) for pixel in diff.getdata())

            if progress_callback:
                progress_callback((total_pages_done + i + 1) / total_pages)

            if diff_score > 1:
                return True, i + 1

        return False, None

    except Exception as e:
        print(f"[{name}] Bildjämförelse fel:", e)
        return False, None

def file_icon(filename):
    return "📄" if filename.lower().endswith(".pdf") else "🧼"

if file_a and file_b:
    if st.button("🔍 Jämför"):
        st.markdown("🚀 **Analys startar – scrolla ner för resultat...**")

        pdfs_a = extract_pdfs(file_a)
        pdfs_b = extract_pdfs(file_b)
        all_names = sorted(set(pdfs_a.keys()).union(set(pdfs_b.keys())))

        # Räkna totalt antal sidor som ska jämföras
        total_pages = 0
        page_counts = {}
        for name in all_names:
            if name in pdfs_a and name in pdfs_b:
                try:
                    num = min(len(fitz.open(pdfs_a[name])), len(fitz.open(pdfs_b[name])))
                    page_counts[name] = num
                    total_pages += num
                except:
                    page_counts[name] = 0

        # Progressbar med jämn uppdatering
        progress_placeholder = st.empty()
        progress_bar = progress_placeholder.progress(0.0)
        pages_done = 0

        def update_progress(pages_done, total_pages):
            progress = pages_done / total_pages if total_pages else 1.0
            progress_bar.progress(progress)
            time.sleep(0.001)  # säkerställer att UI inte fryser

        st.markdown("### 📋 Jämförelsetabell")
        header = st.columns([4, 2, 2, 2, 3])
        header[0].markdown("**Filnamn**")
        header[1].markdown("**I Version A**")
        header[2].markdown("**I Version B**")
        header[3].markdown("**Skillnad i innehåll**")
        header[4].markdown("**Typ av skillnad**")

        for name in all_names:
            in_a = name in pdfs_a
            in_b = name in pdfs_b
            row = st.columns([4, 2, 2, 2, 3])

            with row[0]: st.write(f"{file_icon(name)} {name}")
            with row[1]: st.write("✅ Ja" if in_a else "❌ Nej")
            with row[2]: st.write("✅ Ja" if in_b else "❌ Nej")

            result_placeholder = row[3].empty()
            type_placeholder = row[4].empty()

            if in_a and in_b:
                path_a = pdfs_a[name]
                path_b = pdfs_b[name]

                text_changed = compare_text(path_a, path_b)
                if text_changed:
                    result_placeholder.write("⚠️")
                    type_placeholder.write("Text ändrad")
                    pages_done += page_counts.get(name, 0)
                    update_progress(pages_done, total_pages)
                else:
                    def progress_callback(progress_fraction):
                        progress_bar.progress(progress_fraction)
                        time.sleep(0.001)

                    img_changed, page = compare_images(
                        path_a,
                        path_b,
                        progress_callback=progress_callback,
                        total_pages_done=pages_done,
                        total_pages=total_pages
                    )
                    pages_done += page_counts.get(name, 0)
                    update_progress(pages_done, total_pages)

                    if img_changed:
                        result_placeholder.write("⚠️")
                        type_placeholder.write(f"Bild ändrad (sida {page})")
                    else:
                        result_placeholder.write("–")
                        type_placeholder.write("–")
            else:
                result_placeholder.write("–")
                type_placeholder.write("Saknas i B" if in_a and not in_b else "Saknas i A" if in_b and not in_a else "–")
else:
    st.info("Ladda upp två filer för att kunna jämföra.")
