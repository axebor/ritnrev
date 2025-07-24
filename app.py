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

# Simulerad innehållsskillnad (ersätts senare med riktig jämförelse)
def simulate_diff_type(filename):
    if "berakning" in filename.lower():
        return "Text ändrad"
    elif "ritning" in filename.lower():
        return "Bild/ritning ändrad"
    else:
        return None

if file_a and file_b:
    if st.button("🔍 Jämför"):
        names_a = extract_pdf_names(file_a)
        names_b = extract_pdf_names(file_b)

        all_files = sorted(set(names_a).union(set(names_b)))

        st.markdown("### 📋 Jämförelsetabell")

        header = st.columns([4, 2, 2, 2, 3])
        header[0].markdown("**Filnamn**")
        header[1].markdown("**I Version A**")
        header[2].markdown("**I Version B**")
        header[3].markdown("**Skillnad i innehåll**")
        header[4].markdown("**Typ av skillnad**")

        for name in all_files:
            in_a = name in names_a
            in_b = name in names_b
            row = st.columns([4, 2, 2, 2, 3])

            with row[0]:
                st.write(f"{file_icon(name)} {name}")
            with row[1]:
                st.write("✅ Ja" if in_a else "❌ Nej")
            with row[2]:
                st.write("✅ Ja" if in_b else "❌ Nej")

            if in_a and in_b:
                diff_type = simulate_diff_type(name)
                with row[3]:
                    st.write("⚠️" if diff_type else "–")
                with row[4]:
                    st.write(diff_type if diff_type else "–")
            else:
                with row[3]:
                    st.write("–")
                with row[4]:
                    st.write("Saknas i B" if in_a and not in_b else "Saknas i A" if in_b and not in_a else "–")
else:
    st.info("Ladda upp två filer för att kunna jämföra.")
