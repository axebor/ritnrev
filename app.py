import streamlit as st
from uuid import uuid4

# --- Grundinställningar ---
st.set_page_config(page_title="RitnRev", layout="wide")

# --- Session state init ---
if "projects" not in st.session_state:
    st.session_state.projects = {}
if "active_project" not in st.session_state:
    st.session_state.active_project = None
if "show_project_form" not in st.session_state:
    st.session_state.show_project_form = False

# --- Hjälpfunktioner ---
def add_project(name, desc):
    pid = str(uuid4())
    st.session_state.projects[pid] = {
        "name": name,
        "description": desc,
        "revisions": []
    }
    st.session_state.active_project = pid
    st.session_state.show_project_form = False

def delete_project(pid):
    st.session_state.projects.pop(pid, None)
    if st.session_state.active_project == pid:
        st.session_state.active_project = None

# --- Sidopanel ---
st.sidebar.title("📁 Projekt")
if st.sidebar.button("➕ Nytt projekt"):
    st.session_state.show_project_form = True

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Dina projekt")
for pid, pdata in st.session_state.projects.items():
    c1, c2 = st.sidebar.columns([5,1])
    with c1:
        if st.button(pdata["name"], key=pid):
            st.session_state.active_project = pid
    with c2:
        if st.button("✕", key=f"del_{pid}", help="Ta bort projekt"):
            delete_project(pid)

# --- Huvudområde ---
st.title("RitnRev")

# Om vi är i "nytt projekt"-läge, visa formulär här
if st.session_state.show_project_form:
    st.header("Skapa nytt projekt")
    with st.form("project_form"):
        name = st.text_input("Projektnamn")
        desc = st.text_area("Beskrivning")
        c1, c2 = st.columns([1,1])
        with c1:
            submitted = st.form_submit_button("Skapa projekt")
        with c2:
            canceled = st.form_submit_button("Stäng")
        if canceled:
            st.session_state.show_project_form = False
        if submitted and name:
            add_project(name, desc)

    st.markdown("---")
    st.info("Fyll i formuläret ovan för att skapa ett projekt.")

# Annars, visar vi det valda projektet (eller en uppmaning)
elif st.session_state.active_project:
    proj = st.session_state.projects[st.session_state.active_project]
    st.subheader(f"📄 Projekt: {proj['name']}")
    st.write(proj["description"])
    st.markdown("### 📌 Revisioner")
    if not proj["revisions"]:
        st.info("Inga revisioner ännu.")
    else:
        for rev in proj["revisions"]:
            with st.expander(f"🔍 {rev['title']}"):
                st.write(rev["note"])
    if st.button("➕ Skapa ny revision"):
        st.session_state.show_revision_form = True

    # Här kan du lägga in samma logik för revision-formulär i huvudområdet
else:
    st.info("Välj eller skapa ett projekt i sidomenyn för att börja.")
