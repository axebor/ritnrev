import streamlit as st
from uuid import uuid4

st.set_page_config(page_title="RitnRev", layout="wide")

# --- Initiera state ---
if "projects" not in st.session_state:
    st.session_state.projects = {}
if "active_project" not in st.session_state:
    st.session_state.active_project = None
if "create_project_mode" not in st.session_state:
    st.session_state.create_project_mode = False
if "create_revision_mode" not in st.session_state:
    st.session_state.create_revision_mode = False

# --- Hjälpfunktioner ---
def add_project_callback():
    name = st.session_state._new_proj_name.strip()
    desc = st.session_state._new_proj_desc
    if name:
        pid = str(uuid4())
        st.session_state.projects[pid] = {
            "name": name,
            "description": desc,
            "revisions": []
        }
        st.session_state.active_project = pid
    st.session_state.create_project_mode = False

def add_revision_callback(pid):
    title = st.session_state._new_rev_title.strip()
    note  = st.session_state._new_rev_note
    files = st.session_state._new_rev_files
    if title:
        st.session_state.projects[pid]["revisions"].append({
            "title": title,
            "note": note,
            "files": files
        })
    st.session_state.create_revision_mode = False

def delete_project(pid):
    st.session_state.projects.pop(pid, None)
    if st.session_state.active_project == pid:
        st.session_state.active_project = None

def delete_revision(pid, idx):
    st.session_state.projects[pid]["revisions"].pop(idx)

# --- Sidebar ---
st.sidebar.title("📁 Projekt")
if st.sidebar.button("➕ Skapa nytt projekt"):
    st.session_state.create_project_mode = True
    st.session_state.create_revision_mode = False

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Dina projekt")
for pid, pdata in st.session_state.projects.items():
    c1, c2 = st.sidebar.columns([5,1])
    with c1:
        if st.button(pdata["name"], key=pid):
            st.session_state.active_project = pid
            st.session_state.create_project_mode = False
            st.session_state.create_revision_mode = False
    with c2:
        if st.button("✕", key=f"delproj_{pid}", help="Ta bort projekt"):
            delete_project(pid)

# --- Huvudarea ---
# Visa titel bara om ej i create_project_mode
if not st.session_state.create_project_mode:
    st.title("RitnRev")

# 1) Skapa projekt-läge (utan st.form)
if st.session_state.create_project_mode:
    st.subheader("Skapa nytt projekt")
    st.text_input("Projektnamn", key="_new_proj_name")
    st.text_area("Beskrivning", key="_new_proj_desc")
    c1, c2 = st.columns([1,1])
    with c1:
        st.button("Skapa projekt", on_click=add_project_callback)
    with c2:
        if st.button("Stäng"):
            st.session_state.create_project_mode = False

# 2) Visar valt projekt
elif st.session_state.active_project:
    pid = st.session_state.active_project
    proj = st.session_state.projects[pid]

    st.subheader(f"📄 Projekt: {proj['name']}")
    st.write(proj["description"])
    st.markdown("### 📌 Revisioner")
    if not proj["revisions"]:
        st.info("Inga revisioner ännu.")
    for idx, rev in enumerate(proj["revisions"]):
        with st.expander(rev["title"]):
            st.write(rev["note"])
            st.write(f"Antal filer: {len(rev['files'])}")
            for f in rev["files"]:
                st.write(f"📄 {f.name}")
            if st.button("✕ Ta bort revision", key=f"delrev_{idx}"):
                delete_revision(pid, idx)

    st.markdown("---")
    # Skapa revision-läge
    if st.session_state.create_revision_mode:
        st.subheader("Skapa ny revision")
        st.text_input("Revisionsnamn", key="_new_rev_title")
        st.text_area("Anteckning", key="_new_rev_note")
        st.file_uploader("Ladda upp PDF/ZIP", type=["pdf","zip"],
                         accept_multiple_files=True, key="_new_rev_files")
        r1, r2 = st.columns([1,1])
        with r1:
            st.button("Spara revision", on_click=add_revision_callback, args=(pid,))
        with r2:
            if st.button("Stäng"):
                st.session_state.create_revision_mode = False
    else:
        st.button("➕ Skapa ny revision", on_click=lambda: st.session_state.update(create_revision_mode=True))

# 3) Inget projekt valt
else:
    st.info("Välj eller skapa ett projekt i sidomenyn för att börja.")
