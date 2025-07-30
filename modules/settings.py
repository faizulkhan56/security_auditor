import streamlit as st
def show():
    st.header("Configuration & Settings")
    st.markdown("Configure application settings and preferences.")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**General Settings**")
        st.checkbox("Enable notifications")
        st.checkbox("Auto-save results")
        st.selectbox("Theme", ["Light", "Dark", "Auto"])
    with col2:
        st.markdown("**Security Settings**")
        st.checkbox("Encrypt stored data")
        st.checkbox("Enable API rate limiting")
        st.number_input("Max concurrent scans", 1, 10, 3)
