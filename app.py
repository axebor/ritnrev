import streamlit as st
from uuid import uuid4

st.set_page_config(page_title="RitnRev", layout="wide")

# --- Initiering ---
if "projects" not in st.session_state:
    st.session_state.projects = {}

if "active_project" not in st.session_state:
    st.session_state.active_project = None

if "show_project_form" not in st.session_state:
    st.session_state.show_project_form = False

# --- Skapa projekt ---
def create_project(name, description):
    pid = str(uuid4())
    st.session_state.projects[pid] = {
        "name": name,
        "description": description,
        "revisions": []
    }
    st.session_state.active_project = pid
    st.session_state.show_project_form = False

# --- Ta bort projekt ---
def delete_project(pid):
    if pid in st.session_state.projects:
        del st.session_state.projects[pid]
        if st.session_state.active_project == pid:
            st.session_state.active_project = None

# --- Sidopanel ---
st.sidebar.title("📁 Projekt")

# Knapp: nytt projekt
if st.sidebar.button("➕ Nytt projekt"):
    st.session_state.show_project_form = True

# Formulär: skapa projekt
if st.session_state.show_project_form:
    with st.sidebar:
        st.markdown("""
        <style>
        .close-x {
            font-size: 18px;
            color: #666666;
            cursor: pointer;
            display: inline-block;
            margin-left: 10px;
            transform: translateY(4px);
        }
        .close-x:hover {
            color: #000000;
        }
        </style>
        """, unsafe_allow_html=True)

        with st.form("project_form", border=False):
            name = st.text_input("Projektnamn")
            desc = st.text_area("Beskrivning")

            col1, col2 = st.columns([3, 1])
            with col1:
                submitted = st.form_submit_button("Skapa projekt")
            with col2:
                close = st.markdown(
                    '<div class="close-x" onclick="window.location.reload()">✕</div>',
                    unsafe_allow_html=True
                )

            if submitted and name:
                create_project(name, desc)

# Lista projekt
st.sidebar.markdown("---")
st.sidebar.markdown("📂 **Dina projekt**")
for pid, pdata in list(st.session_state.projects.items()):
    col1, col2 = st.sidebar.columns([5, 1])
    with col1:
        if st.button(pdata["name"], key=f"select_{pid}"):
            st.session_state.active_project = pid
    with col2:
        if st.button("✕", key=f"delete_{pid}"):
            delete_project(pid)

# --- Huvudruta ---
st.title("RitnRev")

if st.session_state.active_project:
    project = st.session_state.projects[st.session_state.active_project]
    st.subheader(f"📄 Projekt: {project['name']}")
    st.write(project["description"])
    st.markdown("### 📌 Revisioner")
    if not project["revisions"]:
        st.info("Inga revisioner ännu.")
    else:
        for rev in project["revisions"]:
            with st.expander(f"🔍 {rev['title']}"):
                st.write(rev["note"])
else:
    st.info("Välj eller skapa ett projekt i menyn till vänster.")
