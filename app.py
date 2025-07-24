import streamlit as st
import uuid

st.set_page_config(layout="wide")

# === INITIERA SESSION STATE ===
if "projects" not in st.session_state:
    st.session_state.projects = {}

if "active_project" not in st.session_state:
    st.session_state.active_project = None

if "create_project_mode" not in st.session_state:
    st.session_state.create_project_mode = False

if "compare_mode" not in st.session_state:
    st.session_state.compare_mode = False


# === FUNKTIONER ===
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


def create_revision(title, date, files):
    rev_id = str(uuid.uuid4())
    st.session_state.projects[st.session_state.active_project]["revisions"][rev_id] = {
        "title": title,
        "date": date,
        "files": files
    }
    st.rerun()


def delete_revision(rid):
    if rid in st.session_state.projects[st.session_state.active_project]["revisions"]:
        del st.session_state.projects[st.session_state.active_project]["revisions"][rid]
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
    project = st.session_state.projects.get(st.session_state.active_project)
    if project:
        st.subheader(f"📄 Projekt: {project['name']}")
        st.caption(project["description"])

        st.markdown("### 📌 Revisioner")

        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("➕ Skapa ny revision", key="create_revision_btn"):
                with st.form("new_rev_form"):
                    title = st.text_input("Titel")
                    date = st.date_input("Datum")
                    uploaded = st.file_uploader("Ladda upp filer", accept_multiple_files=True)
                    submit = st.form_submit_button("Spara")
                    if submit:
                        create_revision(title, str(date), [f.name for f in uploaded])

        with col2:
            if st.button("🔍 Jämför revisioner", key="compare_btn"):
                st.session_state.compare_mode = not st.session_state.compare_mode

        for rid, rdata in project.get("revisions", {}).items():
            with st.expander(f"{rdata['title']}", expanded=True):
                st.write(f"Inkommet underlag {rdata['date']}")
                st.markdown("**Filer:**")
                for fname in rdata["files"]:
                    st.write(f"📄 {fname}")
                if st.button("❌ Ta bort revision", key=f"delrev_{rid}"):
                    delete_revision(rid)

        # === JÄMFÖRELSE ===
        if st.session_state.compare_mode:
            revs = list(project["revisions"].values())
            if len(revs) < 2:
                st.warning("Minst två revisioner krävs för jämförelse.")
            else:
                st.markdown("### 🔍 Resultat av jämförelse")
                old = set(revs[-2]["files"])
                new = set(revs[-1]["files"])
                added = new - old
                removed = old - new

                st.write("**➕ Tillagda filer:**")
                for f in added:
                    st.write(f"📄 {f}")
                st.write("**➖ Borttagna filer:**")
                for f in removed:
                    st.write(f"📄 {f}")

else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
