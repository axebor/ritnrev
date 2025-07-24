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
if "create_revision_mode" not in st.session_state:
    st.session_state.create_revision_mode = False
if "compare_mode" not in st.session_state:
    st.session_state.compare_mode = False
if "compare_selection" not in st.session_state:
    st.session_state.compare_selection = []

# Funktioner
def create_project(name, description):
    project_id = str(uuid.uuid4())
    st.session_state.projects[project_id] = {
        "name": name,
        "description": description,
        "revisions": []
    }
    st.session_state.active_project = project_id
    st.session_state.create_project_mode = False
    st.rerun()

def delete_project(pid):
    if pid in st.session_state.projects:
        del st.session_state.projects[pid]
        if st.session_state.active_project == pid:
            st.session_state.active_project = None
    st.rerun()

def close_project_form():
    st.session_state.create_project_mode = False
    st.rerun()

def create_revision(project_id, title, note, files):
    revision = {
        "id": str(uuid.uuid4()),
        "title": title,
        "note": note,
        "files": files
    }
    st.session_state.projects[project_id]["revisions"].append(revision)
    st.session_state.create_revision_mode = False
    st.rerun()

def delete_revision(project_id, revision_id):
    project = st.session_state.projects[project_id]
    project["revisions"] = [r for r in project["revisions"] if r["id"] != revision_id]
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
                st.session_state.create_revision_mode = False
                st.session_state.compare_mode = False
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
            if st.form_submit_button("Skapa projekt"):
                if name.strip() != "":
                    create_project(name.strip(), description.strip())
                else:
                    st.error("Projektnamn får inte vara tomt!")
        with col2:
            if st.form_submit_button("Stäng"):
                close_project_form()

elif st.session_state.active_project:
    project = st.session_state.projects[st.session_state.active_project]
    st.subheader(f"📄 Projekt: {project['name']}")
    st.write(project["description"])

    # Ny revision
    if st.session_state.create_revision_mode:
        st.markdown("### Skapa ny revision")
        with st.form("create_revision_form"):
            title = st.text_input("Revisionsnamn")
            note = st.text_area("Anteckning / syfte")
            files = st.file_uploader("Ladda upp PDF- eller ZIP-filer", type=["pdf", "zip"], accept_multiple_files=True)

            col1, col2 = st.columns([1, 5])
            with col1:
                if st.form_submit_button("Spara revision"):
                    if title.strip() != "":
                        create_revision(st.session_state.active_project, title.strip(), note, files)
                    else:
                        st.error("Revisionsnamn krävs.")
            with col2:
                if st.form_submit_button("Stäng"):
                    st.session_state.create_revision_mode = False
                    st.rerun()
    else:
        st.button("➕ Skapa ny revision", key="create_revision_btn", on_click=lambda: st.session_state.update(create_revision_mode=True))

    # Jämför revisioner
    if len(project["revisions"]) >= 2:
        st.markdown("### 🧪 Jämför revisioner")
        rev_titles = [rev["title"] for rev in project["revisions"]]
        col1, col2 = st.columns(2)
        with col1:
            rev1 = st.selectbox("Revision 1", rev_titles, key="rev1")
        with col2:
            rev2 = st.selectbox("Revision 2", rev_titles, key="rev2")

        if st.button("🔍 Jämför"):
            r1 = next((r for r in project["revisions"] if r["title"] == rev1), None)
            r2 = next((r for r in project["revisions"] if r["title"] == rev2), None)
            if r1 and r2:
                st.success("Revisioner valda. Här är en enkel jämförelse:")
                st.markdown(f"**{r1['title']}**: {len(r1['files']) if r1['files'] else 0} filer")
                st.markdown(f"**{r2['title']}**: {len(r2['files']) if r2['files'] else 0} filer")
            else:
                st.warning("Kunde inte hitta båda revisionerna.")

    # Visa revisioner
    st.markdown("### 📌 Revisioner")
    for rev in project["revisions"]:
        with st.expander(f"🔍 {rev['title']}"):
            st.write(rev["note"])
            if rev["files"]:
                st.markdown("**Filer:**")
                for f in rev["files"]:
                    st.write(f"📄 {f.name}")
            else:
                st.info("Inga filer uppladdade.")
            if st.button("❌ Ta bort revision", key=f"delrev_{rev['id']}"):
                delete_revision(st.session_state.active_project, rev["id"])

else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
