import streamlit as st
import uuid

# Initiera session_state
if "projects" not in st.session_state:
    st.session_state.projects = {}
if "active_project" not in st.session_state:
    st.session_state.active_project = None
if "create_project_mode" not in st.session_state:
    st.session_state.create_project_mode = False

# Funktioner
def create_project(name, description):
    project_id = str(uuid.uuid4())
    st.session_state.projects[project_id] = {
        "name": name,
        "description": description,
        "revisions": {}
    }
    st.session_state.active_project = project_id
    st.session_state.create_project_mode = False
    st.experimental_rerun()

def delete_project(pid):
    if pid in st.session_state.projects:
        del st.session_state.projects[pid]
        if st.session_state.active_project == pid:
            st.session_state.active_project = None
    st.experimental_rerun()

def close_project_form():
    st.session_state.create_project_mode = False
    st.experimental_rerun()

# Layout
with st.sidebar:
    st.markdown("### 📁 Projekt")
    if st.button("➕ Skapa nytt projekt", key="nytt_projekt"):
        st.session_state.create_project_mode = True
        st.session_state.active_project = None
        st.experimental_rerun()

    st.markdown("---")
    st.markdown("### 📂 Dina projekt")
    for pid, pdata in st.session_state.projects.items():
        c1, c2 = st.columns([5, 1])
        with c1:
            if st.button(pdata["name"], key=f"select_{pid}"):
                st.session_state.active_project = pid
                st.session_state.create_project_mode = False
                st.experimental_rerun()
        with c2:
            if st.button("❌", key=f"delete_{pid}"):
                delete_project(pid)

# Huvudområde
if st.session_state.create_project_mode:
    st.markdown("## Skapa nytt projekt")
    with st.container(border=True):
        name = st.text_input("Projektnamn")
        description = st.text_area("Beskrivning")

        col1, col2 = st.columns([1, 6])
        with col1:
            if st.button("Skapa projekt"):
                if name:
                    create_project(name, description)
        with col2:
            if st.button("Stäng", key="close_form"):
                close_project_form()

elif st.session_state.active_project:
    project = st.session_state.projects[st.session_state.active_project]
    st.markdown(f"## Projekt: {project['name']}")
    st.write(project["description"])
    st.markdown("### 📌 Revisioner")
    if st.button("➕ Skapa ny revision"):
        st.info("Här kommer revisionsformulär så småningom.")
else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
