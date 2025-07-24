import streamlit as st
from uuid import uuid4

st.set_page_config(page_title="RitnRev", layout="wide")

# --- Initiera session ---
if "projects" not in st.session_state:
    st.session_state.projects = {}
if "active_project" not in st.session_state:
    st.session_state.active_project = None
if "show_project_form" not in st.session_state:
    st.session_state.show_project_form = False

# --- Sidomeny: Projektlista och knapp ---
st.sidebar.title("📁 Projekt")
if st.sidebar.button("➕ Nytt projekt"):
    st.session_state.show_project_form = True

st.sidebar.markdown("---")
st.sidebar.markdown("### 📂 Dina projekt")
for pid, pdata in st.session_state.projects.items():
    cols = st.sidebar.columns([6, 1])
    if cols[0].button(pdata["name"], key=f"proj_{pid}"):
        st.session_state.active_project = pid
    if cols[1].button("✕", key=f"del_{pid}"):
        if st.session_state.active_project == pid:
            st.session_state.active_project = None
        del st.session_state.projects[pid]
        st.rerun()

# --- Huvudinnehåll ---
st.title("RitnRev")

# --- Visa "modal" för nytt projekt ---
if st.session_state.show_project_form:
    with st.container():
        st.markdown("""
            <div style="
                position: fixed;
                top: 0; left: 0; right: 0; bottom: 0;
                background-color: rgba(0, 0, 0, 0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;">
              <div style="
                  background-color: white;
                  padding: 2rem;
                  border-radius: 8px;
                  width: 400px;
                  position: relative;">
                <form action="" method="post">
        """, unsafe_allow_html=True)

        with st.form("new_project_form"):
            name = st.text_input("Projektnamn")
            desc = st.text_area("Beskrivning")
            submit = st.form_submit_button("Skapa projekt")

            if submit and name:
                pid = str(uuid4())
                st.session_state.projects[pid] = {
                    "name": name,
                    "description": desc,
                    "revisions": []
                }
                st.session_state.active_project = pid
                st.session_state.show_project_form = False
                st.rerun()

        st.markdown("""
                </form>
                <div style="
                    position: absolute;
                    top: 8px;
                    right: 12px;
                    cursor: pointer;
                    font-size: 20px;
                    color: #666;"
                    onclick="document.forms[0].submit();">
                    <form method='post'>
                      <button name='close' style='border:none;background:none;font-size:20px;color:#666;'>✕</button>
                    </form>
                </div>
              </div>
            </div>
        """, unsafe_allow_html=True)

if st.session_state.active_project:
    project = st.session_state.projects[st.session_state.active_project]
    st.subheader(f"📄 Projekt: {project['name']}")
    st.write(project["description"])
    st.markdown("### 📌 Revisioner")
    if not project["revisions"]:
        st.info("Inga revisioner ännu.")
else:
    st.info("Välj eller skapa ett projekt i menyn för att börja.")
