import streamlit as st
from uuid import uuid4

# --- Anpassad layout & sidomeny-styling ---
st.set_page_config(page_title="RitnRev", layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        min-width: 320px !important;
        max-width: 320px !important;
        width: fit-content !important;
        resize: none !important;
    }
    [data-testid="stSidebar"] section {
        overflow-x: auto;
        white-space: nowrap;
    }

    .revision-knapp {
        margin-left: 2rem;
        font-size: 0.85rem;
        padding: 0.25rem 0.5rem;
        border-radius: 0.5rem;
        border: none;
        background-color: #f0f2f6;
        display: block;
        text-align: left;
        cursor: pointer;
    }
    .revision-knapp:hover {
        background-color: #e2e6ea;
    }
    </style>
""", unsafe_allow_html=True)

# --- Initiera sessionsdata ---
if "projects" not in st.session_state:
    st.session_state.projects = {}

if "active_project" not in st.session_state:
    st.session_state.active_project = None

if "show_project_form" not in st.session_state:
    st.session_state.show_project_form = False

if "show_revision_form" not in st.session_state:
    st.session_state.show_revision_form = False

if "selected_revision" not in st.session_state:
    st.session_state.selected_revision = None


# --- Funktion: välj revision ---
def select_revision(project_id, revision_index):
    st.session_state.active_project = project_id
    st.session_state.selected_revision = revision_index


# --- Sidomeny: Projektträd ---
st.sidebar.title("📁 Projekt")

if st.sidebar.button("➕ Nytt projekt"):
    st.session_state.show_project_form = True

# Formulär för nytt projekt
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
            st.rerun()

# Lista befintliga projekt
for pid, pdata in st.session_state.projects.items():
    with st.sidebar.expander(f"📁 {pdata['name']}", expanded=False):
        if st.button("📂 Öppna projekt", key=f"open_{pid}"):
            st.session_state.active_project = pid
            st.session_state.selected_revision = None
            st.session_state.show_revision_form = False

        for i, rev in enumerate(pdata["revisions"]):
            btn_key = f"{pid}_rev_btn_{i}"
            js = f"""
            <script>
            const btn = document.createElement("button");
            btn.className = "revision-knapp";
            btn.innerText = "📐 {rev['title']}";
            btn.onclick = function() {{
                document.querySelector('[data-testid="{btn_key}"] button').click();
            }};
            document.currentScript.parentElement.appendChild(btn);
            </script>
            """
            st.sidebar.button(" ", key=btn_key, on_click=select_revision, args=(pid, i), help=rev["note"])
            st.sidebar.markdown(js, unsafe_allow_html=True)

# --- Huvudinnehåll ---
st.title("RitnRev")

if st.session_state.active_project:
    project = st.session_state.projects[st.session_state.active_project]
    st.subheader(f"📄 Projekt: {project['name']}")
    st.write(project["description"])

    st.markdown("### 📌 Revisioner")
    for rev in project["revisions"]:
        with st.expander(f"🔍 {rev['title']}"):
            st.write(rev["note"])
            st.write(f"📎 {len(rev['files'])} fil(er) är kopplade:")
            for f in rev["files"]:
                st.write(f"📄 {f.name}")

    st.markdown("---")

    if st.button("➕ Skapa ny revision"):
        st.session_state.show_revision_form = True

    # Formulär för ny revision
    if st.session_state.show_revision_form:
        with st.form("new_revision"):
            rev_title = st.text_input("Revisionsnamn")
            rev_note = st.text_area("Anteckning eller syfte")
            rev_files = st.file_uploader(
                "Ladda upp PDF- eller ZIP-filer",
                type=["pdf", "zip"],
                accept_multiple_files=True
            )
            save = st.form_submit_button("Spara revision")
            if save and rev_title:
                project["revisions"].append({
                    "title": rev_title,
                    "note": rev_note,
                    "files": rev_files
                })
                st.session_state.show_revision_form = False
                st.rerun()
else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
