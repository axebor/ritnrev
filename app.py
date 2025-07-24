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

if "project_created" not in st.session_state:
    st.session_state.project_created = None

# --- Sidomeny ---
st.sidebar.title("📁 Projekt")

# Nytt projekt-knapp
if st.sidebar.button("➕ Nytt projekt"):
    st.session_state.show_project_form = True

# Formulär: skapa projekt
if st.session_state.show_project_form:
    with st.sidebar.container():
        st.markdown(
            """
            <div style='display: flex; justify-content: flex-end; margin-bottom: -1.5em;'>
                <button onclick="window.location.reload()" style='background: none; border: none; color: #555; font-size: 16px; cursor: pointer;'>&#10005;</button>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form("create_project"):
            name = st.text_input("Projektnamn")
            description = st.text_area("Beskrivning")
            cols = st.columns([1, 1])
            with cols[0]:
                create = st.form_submit_button("Skapa projekt")
            with cols[1]:
                cancel = st.form_submit_button("Stäng")

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
                st.session_state.project_created = name
                st.session_state.show_project_form = False

# Lista projekt
if st.session_state.projects:
    st.sidebar.markdown("### 📂 Dina projekt")
    for pid, pdata in st.session_state.projects.items():
        col1, col2 = st.sidebar.columns([5, 1])
        if col1.button(pdata["name"], key=pid):
            st.session_state.active_project = pid
            st.session_state.show_revision_form = False
        if col2.button("🗑️", key=f"delete_{pid}"):
            del st.session_state.projects[pid]
            if st.session_state.active_project == pid:
                st.session_state.active_project = None

# --- Huvudinnehåll ---
st.title("RitnRev")

if st.session_state.active_project:
    project = st.session_state.projects[st.session_state.active_project]

    if st.session_state.project_created == project["name"]:
        st.success(f"Projekt '{project['name']}' skapat!")
        st.session_state.project_created = None

    st.subheader(f"📄 Projekt: {project['name']}")
    st.write(project["description"])

    st.markdown("### 📌 Revisioner")
    for rev in project["revisions"]:
        with st.expander(f"🔍 {rev['title']}"):
            st.write(rev["note"])
            st.write(f"{len(rev['files'])} fil(er) är kopplade.")
            for f in rev["files"]:
                st.write(f"📄 {f.name}")

    st.markdown("---")

    if st.button("➕ Skapa ny revision"):
        st.session_state.show_revision_form = True

    if st.session_state.show_revision_form:
        with st.form("new_revision"):
            rev_title = st.text_input("Revisionsnamn")
            rev_note = st.text_area("Anteckning eller syfte")
            rev_files = st.file_uploader("Ladda upp PDF- eller ZIP-filer", type=["pdf", "zip"], accept_multiple_files=True)
            cols = st.columns([1, 1])
            with cols[0]:
                save = st.form_submit_button("Spara revision")
            with cols[1]:
                cancel = st.form_submit_button("❌ Stäng")

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
