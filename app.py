import streamlit as st
from uuid import uuid4

st.set_page_config(page_title="RitnRev", layout="wide")

# --- Initiera session state ---
if "projects" not in st.session_state:
    st.session_state.projects = {}
if "active_project" not in st.session_state:
    st.session_state.active_project = None
if "create_project_mode" not in st.session_state:
    st.session_state.create_project_mode = False
if "create_revision_mode" not in st.session_state:
    st.session_state.create_revision_mode = False

# --- Hjälpfunktioner ---
def add_project(name, desc):
    pid = str(uuid4())
    st.session_state.projects[pid] = {
        "name": name,
        "description": desc,
        "revisions": []
    }
    st.session_state.active_project = pid

def delete_project(pid):
    st.session_state.projects.pop(pid, None)
    if st.session_state.active_project == pid:
        st.session_state.active_project = None

def add_revision(pid, title, note, files):
    st.session_state.projects[pid]["revisions"].append({
        "title": title,
        "note": note,
        "files": files
    })

def delete_revision(pid, idx):
    st.session_state.projects[pid]["revisions"].pop(idx)

# --- Sidopanel ---
st.sidebar.title("📁 Projekt")

if st.sidebar.button("➕ Skapa nytt projekt"):
    st.session_state.create_project_mode = True
    st.session_state.create_revision_mode = False

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Dina projekt")
for pid, pdata in st.session_state.projects.items():
    col1, col2 = st.sidebar.columns([5,1])
    with col1:
        if st.button(pdata["name"], key=f"select_{pid}"):
            st.session_state.active_project = pid
            st.session_state.create_project_mode = False
            st.session_state.create_revision_mode = False
    with col2:
        if st.button("❌", key=f"delproj_{pid}", help="Ta bort projekt"):
            delete_project(pid)

# --- Huvudarea ---
st.title("RitnRev")

# 1) Skapa projekt-läge
if st.session_state.create_project_mode:
    st.header("Skapa nytt projekt")
    with st.form("project_form"):
        name = st.text_input("Projektnamn")
        desc = st.text_area("Beskrivning")
        c1, c2 = st.columns(2)
        with c1:
            submitted = st.form_submit_button("Skapa projekt")
        with c2:
            canceled = st.form_submit_button("Stäng")
    if canceled:
        st.session_state.create_project_mode = False
    if submitted and name:
        add_project(name, desc)
        st.session_state.create_project_mode = False

# 2) Projekt valt-läge
elif st.session_state.active_project:
    pid = st.session_state.active_project
    project = st.session_state.projects[pid]

    st.subheader(f"📄 Projekt: {project['name']}")
    st.write(project["description"])
    st.markdown("### 📌 Revisioner")

    # Lista befintliga revisioner
    if not project["revisions"]:
        st.info("Inga revisioner ännu.")
    for idx, rev in enumerate(project["revisions"]):
        with st.expander(rev["title"]):
            st.write(rev["note"])
            st.write(f"Antal filer: {len(rev['files'])}")
            for f in rev["files"]:
                st.write(f"📄 {f.name}")
            if st.button("❌ Ta bort revision", key=f"delrev_{idx}"):
                delete_revision(pid, idx)

    st.markdown("---")
    # Skapa revision-läge
    if st.session_state.create_revision_mode:
        st.subheader("Skapa ny revision")
        with st.form("revision_form"):
            title = st.text_input("Revisionsnamn")
            note = st.text_area("Anteckning eller syfte")
            files = st.file_uploader("Ladda upp PDF- eller ZIP-filer", 
                                     type=["pdf", "zip"], 
                                     accept_multiple_files=True)
            c1, c2 = st.columns(2)
            with c1:
                rev_sub = st.form_submit_button("Spara revision")
            with c2:
                rev_cancel = st.form_submit_button("Stäng")
        if rev_cancel:
            st.session_state.create_revision_mode = False
        if rev_sub and title:
            add_revision(pid, title, note, files)
            st.session_state.create_revision_mode = False
    else:
        if st.button("➕ Skapa ny revision"):
            st.session_state.create_revision_mode = True

# 3) Ingen projekt valt
else:
    st.info("Välj eller skapa ett projekt i sidomenyn för att börja.")
