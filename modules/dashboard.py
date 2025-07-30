import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def show():
    st.header("Dashboard")
    st.markdown("**Summary of Recent Scans & Vulnerabilities**")
    # demo data for the dashboard
    scan_data = {
        "Date": ["2024-01-15", "2024-01-14", "2024-01-13"],
        "Model": ["GPT-3.5-turbo", "Llama3:8b", "GPT-4"],
        "Vulnerabilities": [3, 7, 1],
        "Score": [8.5, 6.2, 9.1]
    }
    df = pd.DataFrame(scan_data)
    st.dataframe(df, use_container_width=True)

    st.subheader("Scan Vulnerabilities Bar Chart")
    st.bar_chart(df.set_index("Model")["Vulnerabilities"])

    st.subheader("Security Score Trend")
    st.line_chart(df.set_index("Date")["Score"])
