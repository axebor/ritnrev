import streamlit as st
import os
import zipfile
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
def reset_project_form():
    st.session_state.show_project_form = False

def delete_project(pid):
    if pid in st.session_state.projects:
        del st.session_state.projects[pid]
        if st.session_state.active_project == pid:
            st.session_state.active_project = None

# --- Sidomeny ---
st.sidebar.markdown("## \U0001F4C1 Projekt")

# Nytt projekt-knapp
if st.sidebar.button("➕ Nytt projekt"):
    st.session_state.show_project_form = True

# Formulär: skapa projekt
if st.session_state.show_project_form:
    with st.sidebar.container(border=True):
        cols = st.columns([10, 1])
        with cols[1]:
            if st.button("❌", key="close_project_form", help="Stäng", use_container_width=True):
                reset_project_form()

        with st.form("create_project_form"):
            name = st.text_input("Projektnamn")
            description = st.text_area("Beskrivning")
            create = st.form_submit_button("Skapa projekt")

            if create and name:
                project_id = str(uuid4())
                st.session_state.projects[project_id] = {
                    "name": name,
                    "description": description,
                    "revisions": []
                }
                st.session_state.active_project = project_id
                reset_project_form()

# Lista projekt
if st.session_state.projects:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### \U0001F4C1 Dina projekt")
    for pid, pdata in list(st.session_state.projects.items()):
        cols = st.sidebar.columns([6, 1])
        with cols[0]:
            if st.button(pdata["name"], key=f"select_{pid}"):
                st.session_state.active_project = pid
                st.session_state.show_revision_form = False
        with cols[1]:
            if st.button("❌", key=f"delete_{pid}", help="Ta bort projekt", use_container_width=True):
                delete_project(pid)

# --- Huvudinnehåll ---
st.title("RitnRev")

if st.session_state.active_project:
    project = st.session_state.projects[st.session_state.active_project]
    st.subheader(f"\U0001F4C4 Projekt: {project['name']}")
    st.write(project["description"])

    st.markdown("### \U0001F4CC Revisioner")
    for rev in project["revisions"]:
        with st.expander(f"🔍 {rev['title']}"):
            st.write(rev["note"])
            st.write(f"{len(rev['files'])} fil(er) är kopplade.")
            for f in rev["files"]:
                st.write(f"📄 {f.name}")

    st.markdown("---")

    # Ny revision
    if st.button("➕ Skapa ny revision"):
        st.session_state.show_revision_form = True

    # Formulär: skapa revision
    if st.session_state.show_revision_form:
        with st.form("new_revision"):
            rev_title = st.text_input("Revisionsnamn")
            rev_note = st.text_area("Anteckning eller syfte")
            rev_files = st.file_uploader("Ladda upp PDF- eller ZIP-filer", type=["pdf", "zip"], accept_multiple_files=True)
            save = st.form_submit_button("Spara revision")

            if save and rev_title:
                revision = {
                    "title": rev_title,
                    "note": rev_note,
                    "files": rev_files
                }
                project["revisions"].append(revision)
                st.session_state.show_revision_form = False
else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
