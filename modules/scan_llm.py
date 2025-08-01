import streamlit as st
from modules import garak_scanner, promptfoo_scanner, chat


def show():
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🛡️ Garak Scanner", "🔍 Promptfoo Scanner", "💬 AI Chat"])

    with tab1:
        garak_scanner.show()

    with tab2:
        promptfoo_scanner.show()

    with tab3:
        chat.show()