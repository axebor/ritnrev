import streamlit as st
from uuid import uuid4

st.set_page_config(page_title="RitnRev", layout="wide")

# --- Initiera session ---
if "projects" not in st.session_state:
    st.session_state.projects = {}

if "active_project" not in st.session_state:
    st.session_state.active_project = None

if "show_project_form" not in st.session_state:
    st.session_state.show_project_form = False

if "show_revision_form" not in st.session_state:
    st.session_state.show_revision_form = False

# --- Funktioner ---
def delete_project(pid):
    st.session_state.projects.pop(pid, None)
    if st.session_state.active_project == pid:
        st.session_state.active_project = None

def delete_revision(project_id, index):
    st.session_state.projects[project_id]["revisions"].pop(index)

# --- Sidomeny ---
st.sidebar.title("📁 Projekt")

if st.sidebar.button("➕ Nytt projekt"):
    st.session_state.show_project_form = True
    st.session_state.show_revision_form = False

if st.session_state.show_project_form:
    with st.sidebar.form("create_project"):
        name = st.text_input("Projektnamn")
        description = st.text_area("Beskrivning")
        col1, col2 = st.columns(2)
        create = col1.form_submit_button("Skapa projekt")
        cancel = col2.form_submit_button("❌ Stäng")

        if cancel:
            st.session_state.show_project_form = False

        if create and name:
            project_id = str(uuid4())
            st.session_state.projects[project_id] = {
                "name": name,
                "description": description,
                "revisions": []
            }
            st.session_state.active_project = project_id
            st.session_state.show_project_form = False
            st.success(f"Projekt '{name}' skapat!")

# Lista projekt
if st.session_state.projects:
    st.sidebar.markdown("----")
    st.sidebar.subheader("📂 Dina projekt")
    for pid, pdata in st.session_state.projects.items():
        col1, col2 = st.sidebar.columns([5, 1])
        if col1.button(pdata["name"], key=f"proj_{pid}"):
            st.session_state.active_project = pid
            st.session_state.show_revision_form = False
        if col2.button("🗑️", key=f"del_{pid}"):
            delete_project(pid)

# --- Huvudfönster ---
st.title("RitnRev")

if st.session_state.active_project:
    pid = st.session_state.active_project
    project = st.session_state.projects[pid]

    st.subheader(f"📄 Projekt: {project['name']}")
    st.write(project["description"])

    st.markdown("### 📌 Revisioner")
    for i, rev in enumerate(project["revisions"]):
        with st.expander(f"🔍 {rev['title']}"):
            st.write(rev["note"])
            st.write(f"{len(rev['files'])} fil(er) är kopplade.")
            for f in rev["files"]:
                st.write(f"📄 {f.name}")
            if st.button("🗑️ Ta bort revision", key=f"delrev_{i}"):
                delete_revision(pid, i)

    st.markdown("---")

    if st.button("➕ Skapa ny revision"):
        st.session_state.show_revision_form = True

    if st.session_state.show_revision_form:
        with st.form("create_revision"):
            rev_title = st.text_input("Revisionsnamn")
            rev_note = st.text_area("Anteckning eller syfte")
            rev_files = st.file_uploader("Ladda upp PDF- eller ZIP-filer", type=["pdf", "zip"], accept_multiple_files=True)
            col1, col2 = st.columns(2)
            save = col1.form_submit_button("Spara revision")
            cancel = col2.form_submit_button("❌ Stäng")

            if cancel:
                st.session_state.show_revision_form = False

            if save and rev_title:
                revision = {
                    "title": rev_title,
                    "note": rev_note,
                    "files": rev_files
                }
                project["revisions"].append(revision)
                st.session_state.show_revision_form = False
                st.success(f"Revision '{rev_title}' skapad!")

else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
