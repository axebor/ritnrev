import streamlit as st
import base64

st.set_page_config(layout="centered")
st.title("📄 Compare PDF Content")

# PDF-ikon (konverterad till base64)
pdf_icon_base64 = "iVBORw0KGgoAAAANSUhEUgAAACoAAAAsCAYAAADwEswLAAAACXBIWXMAAAsTAAALEwEAmpwYAAABUUlEQVR4nO2YQUoDQRRF/0Yys1HyKkEJpV0pyD8lM+hg1T0AS9gpzv7DwIQK1qTiG8d3HD/MdAx4Sm+znQCIgiAIgiAIgiAIgiAIgt8BG9Bd9SuDADrsD3rszBaE9p9jTxDxeyS9n2NHMYDuoyM4wAZzgDzmt9EDP8gGXaXEQWc1QJeP8ERHcFM8yNcCGcIhQL3WAVUG4CMcI7ULZQnLyz7r6q0v+NTV64xHaHwQ2NpyAgbFSy2mnkNaVxPy9Xz+gI/xULIJZx+AHmi+ILaOq0svfHXB0pRBmbs7px+jv95DT+M3zw2s4acVbRUX9/jBDv3S0fz+z09X0feQ92EBt/tY2QYjAAAAAElFTkSuQmCC"

# Funktion för att visa filnamn med ikon
def display_file_with_icon(file):
    icon_html = f'<img src="data:image/png;base64,{pdf_icon_base64}" width="20" style="margin-right: 6px; vertical-align: middle;" />'
    st.markdown(f"{icon_html} **{file.name}**", unsafe_allow_html=True)

# Filuppladdning
col1, col2 = st.columns(2)

with col1:
    file1 = st.file_uploader("Upload first PDF", type="pdf", key="file1")

with col2:
    file2 = st.file_uploader("Upload second PDF", type="pdf", key="file2")

# Visa filinformation
if file1 and file2:
    st.markdown("---")
    st.subheader("📂 Selected Files")
    display_file_with_icon(file1)
    display_file_with_icon(file2)

    st.markdown("---")
    st.button("🔍 Compare content", use_container_width=True)

elif file1 or file2:
    st.info("Please upload two PDF files to compare.")
else:
    st.info("Upload two PDF files for comparison.")
