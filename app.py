import streamlit as st
from uuid import uuid4
from datetime import datetime

# --- Sidinställningar ---
st.set_page_config(page_title="RitnRev", layout="wide")

# --- Initiera sessionsdata ---
if "projects" not in st.session_state:
    st.session_state.projects = {}
if "active_project" not in st.session_state:
    st.session_state.active_project = None
if "show_project_form" not in st.session_state:
    st.session_state.show_project_form = False
if "show_revision_form" not in st.session_state:
    st.session_state.show_revision_form = False

# --- Sidomeny ---
st.sidebar.title("📁 Projekt")

# Nytt projekt
if st.sidebar.button("➕ Skapa nytt projekt"):
    st.session_state.show_project_form = True

if st.session_state.show_project_form:
    with st.sidebar.form("create_project"):
        name = st.text_input("Projektnamn")
        description = st.text_area("Beskrivning")
        create = st.form_submit_button("Skapa projekt")
        if create and name:
            pid = str(uuid4())
            st.session_state.projects[pid] = {
                "name": name,
                "description": description,
                "revisions": []
            }
            st.session_state.active_project = pid
            st.session_state.show_project_form = False
            st.experimental_rerun()

# Lista befintliga projekt
for pid, pdata in st.session_state.projects.items():
    if st.sidebar.button(f"📂 {pdata['name']}", key=f"open_{pid}"):
        st.session_state.active_project = pid
        st.session_state.show_revision_form = False
        st.experimental_rerun()

# --- Huvudinnehåll ---
st.title("🗂 RitnRev – Projekthantering")

if st.session_state.active_project:
    project = st.session_state.projects[st.session_state.active_project]

    st.subheader(f"📄 {project['name']}")
    st.write(project["description"])
    st.markdown(f"**Antal revisioner:** {len(project['revisions'])}")
    st.divider()

    # Visa revisioner
    if project["revisions"]:
        st.markdown("### 🔁 Revisioner")
        for rev in sorted(project["revisions"], key=lambda r: r["created"], reverse=True):
            with st.container():
                st.markdown(f"**📐 {rev['title']}**  \n_{rev['created'].strftime('%Y-%m-%d %H:%M')}_", help=rev["note"])
                if rev["files"]:
                    for f in rev["files"]:
                        st.write(f"📎 {f.name}")
                st.markdown("---")
    else:
        st.info("Inga revisioner har skapats ännu.")

    # Skapa ny revision
    st.markdown("### ➕ Skapa ny revision")

    if st.session_state.show_revision_form or st.button("➕ Ny revision"):
        st.session_state.show_revision_form = True

    if st.session_state.show_revision_form:
        with st.form("new_revision"):
            title = st.text_input("Revisionsnamn")
            note = st.text_area("Anteckning (valfritt)")
            files = st.file_uploader("Ladda upp PDF- eller ZIP-filer", type=["pdf", "zip"], accept_multiple_files=True)
            save = st.form_submit_button("Spara revision")

            if save and title:
                project["revisions"].append({
                    "title": title,
                    "note": note,
                    "files": files,
                    "created": datetime.now()
                })
                st.session_state.show_revision_form = False
                st.experimental_rerun()

else:
    st.info("Skapa eller välj ett projekt i sidomenyn för att börja.")
