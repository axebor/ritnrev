import streamlit as st
import os
import zipfile
import tempfile
import pdfplumber
from difflib import SequenceMatcher
from pdf2image import convert_from_bytes
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
    """Returnerar dict: {filnamn.pdf: full_path}"""
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
    except Exception as e:
        st.error(f"Fel vid textutvinning från {path}: {e}")
        return ""

def compare_text(path_a, path_b, threshold=0.98):
    text_a = extract_text(path_a)
    text_b = extract_text(path_b)
    ratio = SequenceMatcher(None, text_a, text_b).ratio()
    st.write(f"Textjämförelse för {os.path.basename(path_a)}: Likhet = {ratio:.2%}")
    return ratio < threshold

def compare_images(path_a, path_b, dpi=150, threshold=10000):
    try:
        with open(path_a, "rb") as f1, open(path_b, "rb") as f2:
            images_a = convert_from_bytes(f1.read(), dpi=dpi)
            images_b = convert_from_bytes(f2.read(), dpi=dpi)

        num_pages = min(len(images_a), len(images_b))
        for i in range(num_pages):
            img_a = images_a[i].convert("RGB")
            img_b = images_b[i].convert("RGB")

            if img_a.size != img_b.size:
                st.warning(f"Sida {i+1}: Bilderna har olika storlekar. Skalar om till minsta storlek.")
                min_size = (min(img_a.size[0], img_b.size[0]), min(img_a.size[1], img_b.size[1]))
                img_a = img_a.resize(min_size, Image.Resampling.LANCZOS)
                img_b = img_b.resize(min_size, Image.Resampling.LANCZOS)

            diff = ImageChops.difference(img_a, img_b)
            diff_score = sum(sum(pixel) for pixel in diff.getdata()) / (img_a.size[0] * img_a.size[1])  # Normaliserad diff_score
            st.write(f"[{os.path.basename(path_a)}] Sida {i+1} – diff_score: {diff_score:.2f}")

            if diff_score > threshold:
                return True, i + 1, img_a, img_b, diff_score
        return False, None, None, None, 0
    except Exception as e:
        st.error(f"Fel vid bildjämförelse för {path_a}: {str(e)}. Kontrollera att poppler är installerat och i PATH.")
        return False, None, None, None, 0

def file_icon(filename):
    return "📄" if filename.lower().endswith(".pdf") else "🗜️"

if file_a and file_b:
    if st.button("🔍 Jämför"):
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

        for name in all_names:
            in_a = name in pdfs_a
            in_b = name in pdfs_b
            row = st.columns([4, 2, 2, 2, 3])

            with row[0]: st.write(f"{file_icon(name)} {name}")
            with row[1]: st.write("✅ Ja" if in_a else "❌ Nej")
            with row[2]: st.write("✅ Ja" if in_b else "❌ Nej")

            if in_a and in_b:
                path_a = pdfs_a[name]
                path_b = pdfs_b[name]
                text_changed = compare_text(path_a, path_b)
                img_changed, page, img_a, img_b, score = compare_images(path_a, path_b)

                if text_changed or img_changed:
                    with row[3]: st.write("⚠️")
                    if text_changed and img_changed:
                        with row[4]: st.write(f"Text och bild ändrad (sida {page}) – diff_score: {score:.2f}")
                    elif text_changed:
                        with row[4]: st.write("Text ändrad")
                    elif img_changed:
                        with row[4]: st.write(f"Bild ändrad (sida {page}) – diff_score: {score:.2f}")
                    if img_changed:
                        with st.expander(f"🔍 Visa skillnad (sida {page})"):
                            col1, col2 = st.columns(2)
                            col1.image(img_a, caption="Version A")
                            col2.image(img_b, caption="Version B")
                else:
                    with row[3]: st.write("–")
                    with row[4]: st.write("Ingen skillnad")
            else:
                with row[3]: st.write("–")
                with row[4]:
                    st.write("Saknas i B" if in_a and not in_b else "Saknas i A" if in_b and not in_a else "–")
else:
    st.info("Ladda upp två filer för att kunna jämföra.")
