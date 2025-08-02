import json
import warnings

import streamlit as st
from streamlit_lottie import st_lottie

from auth import authenticator
from modules import home, scan_llm, dashboard, logs, prompts, settings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="LLM Security Auditor",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for authentication
if 'authentication_status' not in st.session_state:
    st.session_state.authentication_status = None
if 'logout' not in st.session_state:
    st.session_state.logout = False
if 'name' not in st.session_state:
    st.session_state.name = None
if 'username' not in st.session_state:
    st.session_state.username = None

# # Render login widget
try:
    authenticator.login()
except Exception as e:
    st.error(e)

# Authentication check using session state
if st.session_state.get('authentication_status'):

    # Your app content here
    try:
        with open("assets/styles.css", 'r', encoding='utf-8') as f:
            st.html(f"<style>{f.read()}</style>")
    except Exception as e:
        st.warning(f"Could not load CSS: {e}")

    try:
        with open("assets/Red Network Globe.json", 'r', encoding='utf-8') as f:
            lottie_json = json.load(f)
            if lottie_json:
                with st.sidebar:
                    st_lottie(lottie_json, speed=0.5, width=160, key="logo")
    except (FileNotFoundError, json.JSONDecodeError):
        st.sidebar.warning("LLM Security Auditor")
    except Exception as e:
        st.sidebar.error(f"LLM Security Auditor: {e}")

    # Navigation
    page = st.sidebar.radio(
        label="Navigation",
        options=["Home", "Scan", "Dashboard", "Logs", "Prompts", "Settings"],
        index=0,
        format_func=lambda x: f"{x}" if x == "Home" else x
    )

    page_mapping = {
        "Home": home.show,
        "Scan": scan_llm.show,
        "Dashboard": dashboard.show,
        "Logs": logs.show,
        "Prompts": prompts.show,
        "Settings": settings.show
    }

    page_mapping[page]()

    st.html("""
        <style>
        [data-testid="stSidebar"] .stButton {
            position: fixed;
            bottom: 2rem;
            font-size: 8px;
            left: 1.5rem;
            width: 85%;
            z-index: 9999;
        }
        </style>
    """)

    with st.sidebar:
        authenticator.logout('Logout', 'sidebar')

elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')