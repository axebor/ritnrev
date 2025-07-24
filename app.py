import streamlit as st
import os
import zipfile
import tempfile
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

if "last_created_project" not in st.session_state:
    st.session_state.last_created_project = None

# --- Funktioner ---
def delete_project(pid):
    st.session_state.projects.pop(pid, None)
    if st.session_state.active_project == pid:
        st.session_state.active_project = None
        st.session_state.show_project_form = False
        st.session_state.show_revision_form = False

def delete_revision(project_id, index):
    st.session_state.projects[project_id]["revisions"].pop(index)
    st.session_state.show_revision_form = False

# --- Sidomeny ---
st.sidebar.title("📁 Projekt")

# Nytt projekt-knapp
if st.sidebar.button("➕ Nytt projekt"):
    st.session_state.show_project_form = True

# Formulär: skapa projekt
if st.session_state.show_project_form:
    with st.sidebar.form("create_project"):
        name = st.text_input("Projektnamn")
        description = st.text_area("Beskrivning")
        col1, col2 = st.columns(2)
        create = col1.form_submit_button("Skapa projekt")
        cancel = col2.form_submit_button("❌ Stäng")

        if create and name:
            project_id = str(uuid4())
            st.session_state.projects[project_id] = {
                "name": name,
                "description": description,
                "revisions": []
            }
            st.session_state.active_project = project_id
            st.session_state.show_project_form = False
            st.session_state.last_created_project = name

        if cancel:
            st.session_state.show_project_form = False

# Meddelande vid lyckad projekt-skapning
if st.session_state.last_created_project:
    st.sidebar.success(f"Projekt '{st.session_state.last_created_project}' skapat!")
    st.session_state.last_created_project = None

# Lista projekt
if st.session_state.projects:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📂 Dina projekt")
    for pid, pdata in st.session_state.projects.items():
        col1, col2 = st.sidebar.columns([4, 1])
        if col1.button(pdata["name"], key=pid):
            st.session_state.active_project = pid
            st.session_state.show_revision_form = False
        if col2.button("🗑️", key=f"del_{pid}"):
            delete_project(pid)

# --- Huvudinnehåll ---
st.title("RitnRev")

if st.session_state.active_project:
    project_id = st.session_state.active_project
    project = st.session_state.projects[project_id]

    st.subheader(f"📄 Projekt: {project['name']}")
    st.write(project["description"])

    st.markdown("### 📌 Revisioner")
    for i, rev in enumerate(project["revisions"]):
        with st.expander(f"🔍 {rev['title']}"):
            st.write(rev["note"])
            st.write(f"{len(rev['files'])} fil(er) är kopplade.")
            for f in rev["files"]:
                st.write(f"📄 {f.name}")
            if st.button("🗑️ Ta bort revision", key=f"del_rev_{i}"):
                delete_revision(project_id, i)

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
            col1, col2 = st.columns(2)
            save = col1.form_submit_button("Spara revision")
            cancel = col2.form_submit_button("❌ Stäng")

            if save and rev_title:
                revision = {
                    "title": rev_title,
                    "note": rev_note,
                    "files": rev_files
                }
                project["revisions"].append(revision)
                st.session_state.show_revision_form = False
                st.success(f"Revision '{rev_title}' skapad!")

            if cancel:
                st.session_state.show_revision_form = False

else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
