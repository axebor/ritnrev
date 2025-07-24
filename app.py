import streamlit as st
from uuid import uuid4

st.set_page_config(page_title="RitnRev", layout="wide")

# Initiera sessionsdata
if "projects" not in st.session_state:
    st.session_state.projects = {}
if "active_project" not in st.session_state:
    st.session_state.active_project = None
if "show_project_form" not in st.session_state:
    st.session_state.show_project_form = False
if "show_revision_form" not in st.session_state:
    st.session_state.show_revision_form = False

# Sidomeny
st.sidebar.header("📁 Projekt")

if st.sidebar.button("➕ Nytt projekt"):
    st.session_state.show_project_form = True

if st.session_state.show_project_form:
    with st.sidebar.form("project_form"):
        name = st.text_input("Projektnamn")
        desc = st.text_area("Beskrivning")
        submit = st.form_submit_button("Skapa")
        if submit and name:
            pid = str(uuid4())
            st.session_state.projects[pid] = {
                "name": name,
                "desc": desc,
                "revisions": []
            }
            st.session_state.active_project = pid
            st.session_state.show_project_form = False
            st.rerun()

# Lista projekt och revisioner
for pid, project in st.session_state.projects.items():
    st.sidebar.markdown(f"**📁 {project['name']}**")
    if st.sidebar.button("📂 Öppna", key=f"open_{pid}"):
        st.session_state.active_project = pid
        st.session_state.show_revision_form = False

    for i, rev in enumerate(project["revisions"]):
        st.sidebar.markdown(f"<span style='margin-left:1.5em; font-size:0.85rem;'>• {rev['title']}</span>", unsafe_allow_html=True)

    st.sidebar.markdown("")

# Huvudinnehåll
st.title("RitnRev")

if st.session_state.active_project:
    project = st.session_state.projects[st.session_state.active_project]
    st.subheader(f"📄 Projekt: {project['name']}")
    st.write(project["desc"])

    if st.button("➕ Lägg till revision"):
        st.session_state.show_revision_form = True

    if st.session_state.show_revision_form:
        with st.form("rev_form"):
            title = st.text_input("Revisionsnamn")
            note = st.text_area("Kommentar")
            files = st.file_uploader("Ladda upp filer", type=["pdf", "zip"], accept_multiple_files=True)
            save = st.form_submit_button("Spara revision")
            if save and title:
                project["revisions"].append({
                    "title": title,
                    "note": note,
                    "files": files
                })
                st.session_state.show_revision_form = False
                st.rerun()

    st.markdown("### 🗂 Revisioner")
    for rev in project["revisions"]:
        with st.expander(rev["title"]):
            st.write(rev["note"])
            st.write("Filer:")
            for f in rev["files"]:
                st.write(f"📄 {f.name}")
else:
    st.info("Välj ett projekt i menyn eller skapa ett nytt.")
