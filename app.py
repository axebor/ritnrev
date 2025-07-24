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

if "compare_mode" not in st.session_state:
    st.session_state.compare_mode = False

if "compare_selection" not in st.session_state:
    st.session_state.compare_selection = []

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
    st.rerun()

def close_project_form():
    st.session_state.create_project_mode = False
    st.rerun()

# === SIDOMENY ===
with st.sidebar:
    st.markdown("### 📁 Projekt")
    if st.button("➕ Skapa nytt projekt", key="create_project_btn", use_container_width=True):
        st.session_state.create_project_mode = True
        st.session_state.active_project = None
        st.rerun()

    st.markdown("---")
    st.markdown("### 📂 Dina projekt")
    for pid in list(st.session_state.projects.keys()):
        pdata = st.session_state.projects[pid]
        c1, c2 = st.columns([5, 1])
        with c1:
            if st.button(pdata["name"], key=f"select_{pid}"):
                st.session_state.active_project = pid
                st.session_state.create_project_mode = False
                st.session_state.compare_mode = False
                st.session_state.compare_selection = []
                st.rerun()
        with c2:
            if st.button("✕", key=f"delproj_{pid}", help="Ta bort projekt"):
                delete_project(pid)

# === HUVUDFÖNSTER ===
if st.session_state.create_project_mode:
    st.title("Skapa nytt projekt")
    with st.form("create_project_form"):
        name = st.text_input("Projektnamn", key="project_name")
        description = st.text_area("Beskrivning", key="project_description")
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.form_submit_button("Skapa projekt", use_container_width=True):
                if name.strip() != "":
                    create_project(name.strip(), description.strip())
                    st.rerun()
                else:
                    st.error("Projektnamn får inte vara tomt!")
        with col2:
            if st.form_submit_button("Stäng", use_container_width=True):
                close_project_form()

elif st.session_state.active_project:
    project = st.session_state.projects[st.session_state.active_project]
    st.subheader(f"📄 Projekt: {project['name']}")
    st.write(project["description"])

    st.markdown("### 📌 Revisioner")

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("➕ Skapa ny revision", key="create_revision_btn"):
            pass  # logik kommer senare
    with col2:
        if len(project["revisions"]) >= 2:
            if st.button("🔍 Jämför revisioner", key="compare_btn"):
                st.session_state.compare_mode = True
                st.session_state.compare_selection = []

    # Lista revisioner
    for rid, rdata in project["revisions"].items():
        with st.expander(rdata["name"]):
            st.write(f"Inkommet underlag {rdata['date']}")
            st.write("**Filer:**")
            for f in rdata["files"]:
                st.write(f"- {f}")
            if st.button("Ta bort revision", key=f"delrev_{rid}"):
                del project["revisions"][rid]
                st.rerun()
            if st.session_state.compare_mode:
                if st.checkbox("Välj för jämförelse", key=f"comp_{rid}"):
                    if rid not in st.session_state.compare_selection:
                        st.session_state.compare_selection.append(rid)

    # Visa jämförelseläge
    if st.session_state.compare_mode and len(st.session_state.compare_selection) == 2:
        r1, r2 = st.session_state.compare_selection
        st.markdown("---")
        st.markdown(f"### 🤔 Jämförelse mellan '{project['revisions'][r1]['name']}' och '{project['revisions'][r2]['name']}'")
        f1 = project["revisions"][r1]["files"]
        f2 = project["revisions"][r2]["files"]

        st.write("**Filer i båda revisioner:**")
        for f in set(f1).union(f2):
            c = "✅" if f in f1 and f in f2 else "❌"
            st.write(f"{c} {f}")

        if st.button("❌ Avbryt jämförelse"):
            st.session_state.compare_mode = False
            st.session_state.compare_selection = []
            st.rerun()

else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
