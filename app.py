import streamlit as st
import uuid

st.set_page_config(layout="wide")

# Initiera session state
if "projects" not in st.session_state:
    st.session_state.projects = {}
if "active_project" not in st.session_state:
    st.session_state.active_project = None
if "show_modal" not in st.session_state:
    st.session_state.show_modal = False

# --- Funktioner ---
def create_project(name, description):
    pid = str(uuid.uuid4())
    st.session_state.projects[pid] = {
        "name": name,
        "description": description,
        "revisions": []
    }
    st.session_state.active_project = pid
    st.session_state.show_modal = False

def delete_project(pid):
    if pid in st.session_state.projects:
        del st.session_state.projects[pid]
        if st.session_state.active_project == pid:
            st.session_state.active_project = None

# --- Sidopanel ---
st.sidebar.markdown("### 📁 Projekt")
if st.sidebar.button("+ Nytt projekt"):
    st.session_state.show_modal = True

st.sidebar.markdown("---")
st.sidebar.markdown("#### 📁 Dina projekt")
for pid, pdata in st.session_state.projects.items():
    cols = st.sidebar.columns([5, 1])
    if cols[0].button(pdata["name"], key=f"select_{pid}"):
        st.session_state.active_project = pid
    if cols[1].button("x", key=f"delete_{pid}"):
        delete_project(pid)
        st.experimental_rerun()

# --- Modal ---
if st.session_state.show_modal:
    modal_style = """
    <style>
    .modal-overlay {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-color: rgba(0, 0, 0, 0.4);
        z-index: 999;
    }
    .modal-box {
        position: fixed;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 0 20px rgba(0,0,0,0.3);
        width: 400px;
        z-index: 1000;
    }
    .modal-close {
        position: absolute;
        top: 10px; right: 15px;
        font-size: 18px;
        color: #666;
        cursor: pointer;
    }
    </style>
    <div class="modal-overlay"></div>
    <div class="modal-box">
        <span class="modal-close" onclick="document.querySelector('button[data-testid=\'modal-close\']').click()">&times;</span>
        <form action="" method="post">
            <label>Projektnamn</label><br>
            <input name="pname" style="width: 100%; padding: 8px;"><br><br>
            <label>Beskrivning</label><br>
            <textarea name="pdesc" style="width: 100%; height: 100px; padding: 8px;"></textarea><br><br>
            <button type="submit">Skapa projekt</button>
        </form>
        <button style="display:none;" data-testid="modal-close" onClick="">Stäng</button>
    </div>
    """
    st.markdown(modal_style, unsafe_allow_html=True)

    # Hantera formulärdata via JS workaround (ej native stöd ännu)
    pname = st.experimental_get_query_params().get("pname", [""])[0]
    pdesc = st.experimental_get_query_params().get("pdesc", [""])[0]
    if pname:
        create_project(pname, pdesc)
        st.experimental_set_query_params()  # rensa query params
        st.experimental_rerun()

# --- Huvudfönster ---
st.title("RitnRev")
if st.session_state.active_project:
    pdata = st.session_state.projects[st.session_state.active_project]
    st.subheader(f"📄 Projekt: {pdata['name']}")
    st.write(pdata["description"])
    st.markdown("### 📌 Revisioner")
    st.button("+ Skapa ny revision")
else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
