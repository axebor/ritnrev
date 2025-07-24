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

# --- Sidomeny: Projektstruktur med "filträd" ---
st.sidebar.title("📁 Projekt")

if st.sidebar.button("➕ Nytt projekt"):
    st.session_state.show_project_form = True

# Formulär: skapa projekt
if st.session_state.show_project_form:
    with st.sidebar.form("create_project"):
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
            st.session_state.show_project_form = False
            st.rerun()  # Uppdatera vyn direkt

# Visa projektstruktur som "filträd"
if st.session_state.projects:
    for pid, pdata in st.session_state.projects.items():
        with st.sidebar.expander(f"📁 {pdata['name']}", expanded=False):
            if st.sidebar.button("📂 Öppna projekt", key=f"open_{pid}"):
                st.session_state.active_project = pid
                st.session_state.show_revision_form = False

            for i, rev in enumerate(pdata["revisions"]):
                if st.sidebar.button(f"🔄 {rev['title']}", key=f"{pid}_rev_{i}"):
                    st.session_state.active_project = pid  # Kan byggas ut om du vill öppna revision direkt

# --- Huvudinnehåll ---
st.title("RitnRev")

if st.session_state.active_project:
    project = st.session_state.projects[st.session_state.active_project]
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
                st.rerun()

else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
