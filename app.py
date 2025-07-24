import streamlit as st
import uuid
import pdfplumber
import difflib
import pandas as pd
import zipfile
import tempfile
import os

st.set_page_config(layout="wide")

# Initiera session state
if "projects" not in st.session_state:
    st.session_state.projects = {}
if "active_project" not in st.session_state:
    st.session_state.active_project = None
if "create_project_mode" not in st.session_state:
    st.session_state.create_project_mode = False
if "create_revision_mode" not in st.session_state:
    st.session_state.create_revision_mode = False

# Funktioner
def create_project(name, description):
    project_id = str(uuid.uuid4())
    st.session_state.projects[project_id] = {
        "name": name,
        "description": description,
        "revisions": []
    }
    st.session_state.active_project = project_id
    st.session_state.create_project_mode = False
    st.rerun()

def delete_project(pid):
    if pid in st.session_state.projects:
        del st.session_state.projects[pid]
        if st.session_state.active_project == pid:
            st.session_state.active_project = None
    st.rerun()

def close_project_form():
    st.session_state.create_project_mode = False
    st.rerun()

def create_revision(project_id, title, note, files):
    revision_files = []
    for uploaded_file in files or []:
        if uploaded_file.name.endswith('.pdf'):
            revision_files.append(uploaded_file)
        elif uploaded_file.name.endswith('.zip'):
            with tempfile.TemporaryDirectory() as tmp_dir:
                with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)
                    pdf_files = [f for f in os.listdir(tmp_dir) if f.endswith('.pdf')]
                    for pdf in pdf_files:
                        with open(os.path.join(tmp_dir, pdf), 'rb') as f:
                            revision_files.append(f.read())
    revision = {
        "id": str(uuid.uuid4()),
        "title": title,
        "note": note,
        "files": revision_files
    }
    st.session_state.projects[project_id]["revisions"].append(revision)
    st.session_state.create_revision_mode = False
    st.rerun()

def delete_revision(project_id, revision_id):
    project = st.session_state.projects[project_id]
    project["revisions"] = [r for r in project["revisions"] if r["id"] != revision_id]
    st.rerun()

def extract_text_from_pdf(pdf_file):
    """Extrahera text från en PDF-fil med pdfplumber."""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Fel vid läsning av PDF: {e}")
        return ""

def compare_texts(text1, text2):
    """Jämför två textsträngar och returnera skillnader."""
    differ = difflib.Differ()
    diff = list(differ.compare(text1.splitlines(), text2.splitlines()))
    return diff

# === SIDOMENY ===
with st.sidebar:
    st.markdown("### 📁 Projekt")
    if st.button("➕ Skapa nytt projekt", key="create_project_btn", use_container_width=True):
        st.session_state.create_project_mode = True
        st.session_state.active_project = None
        st.rerun()

    st.markdown("---")
    st.markdown("### 📂 Dina projekt")
    for pid in list(st.session_state.projects.keys()):
        pdata = st.session_state.projects[pid]
        c1, c2 = st.columns([5, 1])
        with c1:
            if st.button(pdata["name"], key=f"select_{pid}"):
                st.session_state.active_project = pid
                st.session_state.create_project_mode = False
                st.session_state.create_revision_mode = False
                st.rerun()
        with c2:
            if st.button("✕", key=f"delproj_{pid}", help="Ta bort projekt"):
                delete_project(pid)

# === HUVUDFÖNSTER ===
if st.session_state.create_project_mode:
    st.title("Skapa nytt projekt")
    with st.form("create_project_form"):
        name = st.text_input("Projektnamn", key="project_name")
        description = st.text_area("Beskrivning", key="project_description")
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.form_submit_button("Skapa projekt"):
                if name.strip() != "":
                    create_project(name.strip(), description.strip())
                else:
                    st.error("Projektnamn får inte vara tomt!")
        with col2:
            if st.form_submit_button("Stäng"):
                close_project_form()

elif st.session_state.active_project:
    project = st.session_state.projects[st.session_state.active_project]
    st.subheader(f"📄 Projekt: {project['name']}")
    st.write(project["description"])

    # Ny revision
    if st.session_state.create_revision_mode:
        st.markdown("### Skapa ny revision")
        with st.form("create_revision_form"):
            title = st.text_input("Revisionsnamn")
            note = st.text_area("Anteckning / syfte")
            files = st.file_uploader("Ladda upp PDF- eller ZIP-filer", type=["pdf", "zip"], accept_multiple_files=True)

            col1, col2 = st.columns([1, 5])
            with col1:
                if st.form_submit_button("Spara revision"):
                    if title.strip() != "":
                        create_revision(st.session_state.active_project, title.strip(), note, files)
                    else:
                        st.error("Revisionsnamn krävs.")
            with col2:
                if st.form_submit_button("Stäng"):
                    st.session_state.create_revision_mode = False
                    st.rerun()
    else:
        st.button("➕ Skapa ny revision", key="create_revision_btn", on_click=lambda: st.session_state.update(create_revision_mode=True))

    # Visa revisioner och jämförelse
    st.markdown("### 📌 Revisioner")
    selected_revisions = []
    for rev in project["revisions"]:
        with st.expander(f"🔍 {rev['title']}"):
            st.write(rev["note"])
            if rev["files"]:
                st.markdown("**Filer:**")
                for f in rev["files"]:
                    st.write(f"📄 {f.name if hasattr(f, 'name') else 'PDF från ZIP'}")
            else:
                st.info("Inga filer uppladdade.")
            if st.checkbox("Välj för jämförelse", key=f"select_{rev['id']}"):
                selected_revisions.append(rev)
            if st.button("❌ Ta bort revision", key=f"delrev_{rev['id']}"):
                delete_revision(st.session_state.active_project, rev['id'])

    if len(selected_revisions) == 2 and st.button("Jämför"):
        rev1, rev2 = selected_revisions
        st.markdown("### Jämförelse av revisioner")
        with st.spinner("Jämför filer, det kan ta en stund..."):
            if rev1["files"] and rev2["files"]:
                # Välj PDF-filer om flera finns
                file1_options = [f.name if hasattr(f, 'name') else f"PDF_{i}" for i, f in enumerate(rev1["files"])]
                file2_options = [f.name if hasattr(f, 'name') else f"PDF_{i}" for i, f in enumerate(rev2["files"])]
                file1_idx = st.selectbox("Välj PDF från första revisionen", range(len(rev1["files"])), format_func=lambda x: file1_options[x])
                file2_idx = st.selectbox("Välj PDF från andra revisionen", range(len(rev2["files"])), format_func=lambda x: file2_options[x])

                file1 = rev1["files"][file1_idx]
                file2 = rev2["files"][file2_idx]
                
                text1 = extract_text_from_pdf(file1)
                text2 = extract_text_from_pdf(file2)
                
                if text1 and text2:
                    diff = compare_texts(text1, text2)
                    diff_data = [{"Skillnad": line} for line in diff if line.startswith('+ ') or line.startswith('- ')]
                    if diff_data:
                        df = pd.DataFrame(diff_data)
                        st.dataframe(df)
                        csv = df.to_csv(index=False)
                        st.download_button("Ladda ner skillnader som CSV", csv, f"skillnader_{rev1['title']}_vs_{rev2['title']}.csv")
                    else:
                        st.info("Inga skillnader hittades.")
                else:
                    st.error("Kunde inte extrahera text från en eller båda filerna.")
            else:
                st.error("En eller båda revisionerna saknar filer.")
    elif len(selected_revisions) > 2:
        st.warning("Välj exakt två revisioner för jämförelse.")
    elif len(selected_revisions) == 0:
        st.info("Välj två revisioner att jämföra genom att bocka i dem.")

else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
