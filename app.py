import streamlit as st
import uuid

st.set_page_config(layout="wide")

# Initiera session state
if "projects" not in st.session_state:
    st.session_state.projects = {}

if "active_project" not in st.session_state:
    st.session_state.active_project = None

if "create_project_mode" not in st.session_state:
    st.session_state.create_project_mode = False


def create_project(name, description):
    project_id = str(uuid.uuid4())
    st.session_state.projects[project_id] = {
        "name": name,
        "description": description,
        "revisions": {}
    }
    st.session_state.active_project = project_id
    st.session_state.create_project_mode = False


def delete_project(pid):
    if pid in st.session_state.projects:
        del st.session_state.projects[pid]
        if st.session_state.active_project == pid:
            st.session_state.active_project = None


def close_project_form():
    st.session_state.create_project_mode = False


# === SIDOMENY ===
with st.sidebar:
    st.markdown("### 📁 Projekt")
    if st.button("➕ Skapa nytt projekt", use_container_width=True):
        st.session_state.create_project_mode = True
        st.session_state.active_project = None

    st.markdown("---")
    st.markdown("### 📂 Dina projekt")
    for pid in list(st.session_state.projects.keys()):
        pdata = st.session_state.projects[pid]
        c1, c2 = st.columns([5, 1])
        with c1:
            if st.button(pdata["name"], key=f"select_{pid}"):
                st.session_state.active_project = pid
                st.session_state.create_project_mode = False
        with c2:
            if st.button("✕", key=f"delproj_{pid}", help="Ta bort projekt"):
                delete_project(pid)


# === HUVUDFÖNSTER ===
if st.session_state.create_project_mode:
    st.title("Skapa nytt projekt")
    with st.container():
        with st.form("create_project_form"):
            name = st.text_input("Projektnamn")
            description = st.text_area("Beskrivning")
            col1, col2 = st.columns([1, 5])
            with col1:
                submitted = st.form_submit_button("Skapa projekt")
            with col2:
                cancelled = st.form_submit_button("Stäng", use_container_width=True)

            if submitted and name.strip() != "":
                create_project(name.strip(), description.strip())

            if cancelled:
                close_project_form()

elif st.session_state.active_project:
    project = st.session_state.projects[st.session_state.active_project]
    st.subheader(f"📄 Projekt: {project['name']}")
    st.write(project["description"])

    st.markdown("### 📌 Revisioner")
    st.button("➕ Skapa ny revision")

else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
