import streamlit as st
from uuid import uuid4

st.set_page_config(page_title="RitnRev", layout="wide")

# --- Session state ---
if "projects" not in st.session_state:
    st.session_state.projects = {}
if "active_project" not in st.session_state:
    st.session_state.active_project = None
if "show_modal" not in st.session_state:
    st.session_state.show_modal = False

# --- Helper functions ---
def add_project(name, desc):
    pid = str(uuid4())
    st.session_state.projects[pid] = {"name": name, "description": desc, "revisions": []}
    st.session_state.active_project = pid
    st.session_state.show_modal = False

def delete_project(pid):
    st.session_state.projects.pop(pid, None)
    if st.session_state.active_project == pid:
        st.session_state.active_project = None

# --- Sidebar ---
st.sidebar.title("📁 Projekt")
if st.sidebar.button("➕ Nytt projekt"):
    st.session_state.show_modal = True

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

# --- Modal overlay + box ---
if st.session_state.show_modal:
    # Overlay
    overlay_css = """
    <style>
      .overlay {
        position: fixed; top:0; left:0; right:0; bottom:0;
        background: rgba(0,0,0,0.4); z-index: 98;
      }
      .modal {
        position: fixed; top:50%; left:50%;
        transform: translate(-50%,-50%);
        background: #fff; padding: 2rem; border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2); z-index: 99;
        width: 360px;
      }
      .close-btn {
        position: absolute; top:8px; right:12px;
        font-size: 18px; color:#666; cursor:pointer;
      }
      .close-btn:hover {color:#000;}
    </style>
    <div class="overlay"></div>
    <div class="modal">
      <div class="close-btn" onclick="document.querySelector('button[data-testid=\\'close_modal\\'] button').click()">✕</div>
    """
    st.markdown(overlay_css, unsafe_allow_html=True)

    # Actual form
    with st.container():
        with st.form("modal_project_form"):
            st.text_input("Projektnamn", key="__proj_name")
            st.text_area("Beskrivning", key="__proj_desc")
            cols = st.columns([1,1])
            with cols[0]:
                submitted = st.form_submit_button("Skapa projekt")
            with cols[1]:
                canceled = st.form_submit_button("close_modal", label="Stäng")

            if submitted and st.session_state["__proj_name"].strip():
                add_project(st.session_state["__proj_name"], st.session_state["__proj_desc"])
            if canceled:
                st.session_state.show_modal = False

    # close modal div
    st.markdown("</div>", unsafe_allow_html=True)

# --- Main area ---
st.title("RitnRev")

if st.session_state.active_project:
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
else:
    st.info("Välj eller skapa ett projekt i sidomenyn för att börja.")
