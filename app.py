import streamlit as st
from uuid import uuid4

st.set_page_config(page_title="RitnRev", layout="wide")

# --- Initiera state ---
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
    st.session_state.create_project_mode = False

def delete_project(pid):
    st.session_state.projects.pop(pid, None)
    if st.session_state.active_project == pid:
        st.session_state.active_project = None

# --- Sidopanel ---
st.sidebar.title("📁 Projekt")
if st.sidebar.button("➕ Skapa nytt projekt"):
    st.session_state.create_project_mode = True
    st.session_state.create_revision_mode = False

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Dina projekt")
for pid, pdata in st.session_state.projects.items():
    c1, c2 = st.sidebar.columns([5,1])
    with c1:
        if st.button(pdata["name"], key=pid):
            st.session_state.active_project = pid
            st.session_state.create_project_mode = False
            st.session_state.create_revision_mode = False
    with c2:
        if st.button("✕", key=f"delproj_{pid}", help="Ta bort projekt"):
            delete_project(pid)

# --- Huvudarea ---
# Visa titel bara om vi inte skapar projekt
if not st.session_state.create_project_mode:
    st.title("RitnRev")

# 1) Skapa projekt-läge
if st.session_state.create_project_mode:
    st.subheader("Skapa nytt projekt")
    with st.form("project_form"):
        name = st.text_input("Projektnamn")
        desc = st.text_area("Beskrivning")
        # två kolumner, där Stäng är längst ut åt höger
        c1, c2 = st.columns([1,1])
        with c1:
            submitted = st.form_submit_button("Skapa projekt")
        with c2:
            canceled = st.form_submit_button("Stäng")
    if submitted and name:
        add_project(name, desc)
    elif canceled:
        st.session_state.create_project_mode = False

# 2) Visar valt projekt
elif st.session_state.active_project:
    pid = st.session_state.active_project
    project = st.session_state.projects[pid]

    st.subheader(f"📄 Projekt: {project['name']}")
    st.write(project["description"])
    st.markdown("### 📌 Revisioner")

    if not project["revisions"]:
        st.info("Inga revisioner ännu.")
    for idx, rev in enumerate(project["revisions"]):
        with st.expander(rev["title"]):
            st.write(rev["note"])
            if st.button("✕ Ta bort revision", key=f"delrev_{idx}"):
                project["revisions"].pop(idx)

    st.markdown("---")
    if st.session_state.create_revision_mode:
        st.subheader("Skapa ny revision")
        with st.form("revision_form"):
            title = st.text_input("Revisionsnamn")
            note = st.text_area("Anteckning eller syfte")
            files = st.file_uploader("Ladda upp PDF- eller ZIP-filer",
                                     type=["pdf","zip"],
                                     accept_multiple_files=True)
            r1, r2 = st.columns([1,1])
            with r1:
                rev_sub = st.form_submit_button("Spara revision")
            with r2:
                rev_cancel = st.form_submit_button("Stäng")
        if rev_sub and title:
            project["revisions"].append({
                "title": title,
                "note": note,
                "files": files
            })
            st.session_state.create_revision_mode = False
        elif rev_cancel:
            st.session_state.create_revision_mode = False
    else:
        if st.button("➕ Skapa ny revision"):
            st.session_state.create_revision_mode = True

# 3) Inget projekt valt
else:
    st.info("Välj eller skapa ett projekt i sidomenyn för att börja.")
