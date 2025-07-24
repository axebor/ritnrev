import streamlit as st
import uuid
import pdfplumber
import difflib
import pandas as pd

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
if "compare_revision_mode" not in st.session_state:
    st.session_state.compare_revision_mode = False

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
    revision = {
        "id": str(uuid.uuid4()),
        "title": title,
        "note": note,
        "files": files
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
        st.session_state.compare_revision_mode = False
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
                st.session_state.compare_revision_mode = False
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
    # Jämför revisioner
    elif st.session_state.compare_revision_mode:
        st.markdown("### Jämför revisioner")
        revisions = project["revisions"]
        if len(revisions) < 2:
            st.warning("Du behöver minst två revisioner för att jämföra.")
            if st.button("Stäng", key="close_compare"):
                st.session_state.compare_revision_mode = False
                st.rerun()
        else:
            with st.form("compare_revisions_form"):
                rev_options = {rev["title"]: rev for rev in revisions}
                rev1_title = st.selectbox("Välj första revisionen", list(rev_options.keys()), key="rev1")
                rev2_title = st.selectbox("Välj andra revisionen", list(rev_options.keys()), key="rev2")
                
                # Om revisionerna har flera filer, låt användaren välja vilka
                rev1 = rev_options[rev1_title]
                rev2 = rev_options[rev2_title]
                if rev1["files"] and rev2["files"]:
                    file1_options = [f.name for f in rev1["files"] if f.name.endswith(".pdf")]
                    file2_options = [f.name for f in rev2["files"] if f.name.endswith(".pdf")]
                    if file1_options and file2_options:
                        file1_name = st.selectbox("Välj PDF från första revisionen", file1_options, key="file1")
                        file2_name = st.selectbox("Välj PDF från andra revisionen", file2_options, key="file2")
                    else:
                        st.error("En eller båda revisionerna saknar PDF-filer.")
                        file1_name, file2_name = None, None
                else:
                    st.error("En eller båda revisionerna saknar filer.")
                    file1_name, file2_name = None, None

                if st.form_submit_button("Jämför"):
                    if file1_name and file2_name and rev1_title != rev2_title:
                        # Hitta filobjekten
                        file1 = next(f for f in rev1["files"] if f.name == file1_name)
                        file2 = next(f for f in rev2["files"] if f.name == file2_name)
                        
                        # Extrahera text
                        st.write("Jämför filerna...")
                        text1 = extract_text_from_pdf(file1)
                        text2 = extract_text_from_pdf(file2)
                        
                        if text1 and text2:
                            # Jämför texterna
                            diff = compare_texts(text1, text2)
                            diff_data = [{"Skillnad": line} for line in diff if line.startswith('+ ') or line.startswith('- ')]
                            
                            if diff_data:
                                df = pd.DataFrame(diff_data)
                                st.dataframe(df)
                                # Exportera till CSV
                                csv = df.to_csv(index=False)
                                st.download_button("Ladda ner skillnader som CSV", csv, f"skillnader_{rev1_title}_vs_{rev2_title}.csv")
                            else:
                                st.info("Inga skillnader hittades.")
                        else:
                            st.error("Kunde inte extrahera text från en eller båda filerna.")
                    else:
                        st.error("Välj två olika revisioner och giltiga PDF-filer.")
                
                if st.form_submit_button("Stäng"):
                    st.session_state.compare_revision_mode = False
                    st.rerun()
    else:
        st.button("➕ Skapa ny revision", key="create_revision_btn", on_click=lambda: st.session_state.update(create_revision_mode=True))
        st.button("🔍 Jämför revisioner", key="compare_revision_btn", on_click=lambda: st.session_state.update(compare_revision_mode=True))

    # Visa revisioner
    st.markdown("### 📌 Revisioner")
    for rev in project["revisions"]:
        with st.expander(f"🔍 {rev['title']}"):
            st.write(rev["note"])
            if rev["files"]:
                st.markdown("**Filer:**")
                for f in rev["files"]:
                    st.write(f"📄 {f.name}")
            else:
                st.info("Inga filer uppladdade.")
            if st.button("❌ Ta bort revision", key=f"delrev_{rev['id']}"):
                delete_revision(st.session_state.active_project, rev['id'])

else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
