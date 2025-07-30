import streamlit as st
from modules import home, scan_llm, dashboard, logs, prompts, settings
from streamlit_lottie import st_lottie
import json

st.set_page_config(page_title="LLM Security Auditor", layout="wide", initial_sidebar_state="expanded")
with open("assets/styles.css") as fcss:
    st.markdown(f"<style>{fcss.read()}</style>", unsafe_allow_html=True)
# st.sidebar.image("assets/logo.png", width=120)

with open("assets/Red Network Globe.json", "r") as f:
    lottie_json = json.load(f)
    with st.sidebar:
        st_lottie(lottie_json, speed=0.5, width=160, key="logo")

page = st.sidebar.radio(
    "",
    ["Home", "Scan LLM", "Dashboard", "Log Page", "Prompt Library", "Settings"],
    key="navigation"
)
if page == "Home":
    home.show()
elif page == "Scan LLM":
    scan_llm.show()
elif page == "Dashboard":
    dashboard.show()
elif page == "Log Page":
    logs.show()
elif page == "Prompt Library":
    prompts.show()
elif page == "Settings":
    settings.show()
