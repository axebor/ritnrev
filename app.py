import os
import zipfile
import tempfile
import streamlit as st

st.set_page_config(page_title="RitnRev", layout="wide")

# Sidonavigering
sida = st.sidebar.selectbox("Navigera", ["📤 Ladda upp filer", "📋 Matchade filer", "ℹ️ Om appen"])

def extract_zip_to_temp(zip_file):
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(zip_file, "r") as z:
        z.extractall(temp_dir)
    return temp_dir

def save_uploaded_pdfs(uploaded_files):
    temp_dir = tempfile.mkdtemp()
    for file in uploaded_files:
        file_path = os.path.join(temp_dir, file.name)
        with open(file_path, "wb") as f:
            f.write(file.read())
    return temp_dir

def list_pdfs_in_folder(folder):
    return sorted([
        f for f in os.listdir(folder)
        if f.lower().endswith(".pdf")
    ])

# === Sida: Ladda upp ===
if sida == "📤 Ladda upp filer":
    st.markdown("### Ladda upp två versioner av PDF-filer")
    st.markdown("Du kan ladda upp en .zip-fil **eller** enstaka PDF-filer per version.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔹 Version A")
        zip_a = st.file_uploader("Ladda upp ZIP (eller hoppa över)", type="zip", key="zip_a")
        pdfs_a = st.file_uploader("...eller ladda upp PDF:er direkt", type="pdf", accept_multiple_files=True, key="pdf_a")

    with col2:
        st.markdown("#### 🔸 Version B")
        zip_b = st.file_uploader("Ladda upp ZIP (eller hoppa över)", type="zip", key="zip_b")
        pdfs_b = st.file_uploader("...eller ladda upp PDF:er direkt", type="pdf", accept_multiple_files=True, key="pdf_b")

    if (zip_a or pdfs_a) and (zip_b or pdfs_b):
        st.success("✅ Filer laddade. Gå vidare till '📋 Matchade filer' i menyn.")

    else:
        st.info("Vänligen ladda upp filer för båda versionerna.")

# === Sida: Visa matchning ===
elif sida == "📋 Matchade filer":
    st.markdown("### 📂 Matchade PDF-filer mellan versioner")

    if "zip_a" in st.session_state or "pdf_a" in st.session_state:
        if "zip_b" in st.session_state or "pdf_b" in st.session_state:

            # Hantera version A
            if zip_a:
                dir_a = extract_zip_to_temp(zip_a)
            else:
                dir_a = save_uploaded_pdfs(pdfs_a)

            # Hantera ver
