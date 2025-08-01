import streamlit as st
import os
import json


def show():
    st.markdown("""
    <style>
    .stTextInput > div > div > input {
        font-size: 14px !important;
    }
    .stSelectbox > div > div > div > div {
        font-size: 14px !important;
    }
    h3 {
        font-size: 18px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("### Application Settings")

    # Initialize settings from environment
    if "app_settings" not in st.session_state:
        st.session_state.app_settings = {
            "s3": {
                "bucket": os.getenv("S3_BUCKET", "llm-auditor-reports"),
                "access_key": os.getenv("AWS_ACCESS_KEY_ID", ""),
                "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY", ""),
                "region": os.getenv("AWS_DEFAULT_REGION", "us-east-1")
            },
            "output": {
                "reports_folder": "./reports",
                "logs_folder": "./logs"
            }
        }

    settings = st.session_state.app_settings

    # S3 Configuration
    st.markdown("#### S3 Configuration")

    with st.form("s3_settings"):
        col1, col2 = st.columns(2)

        with col1:
            bucket = st.text_input("Bucket Name", value=settings["s3"]["bucket"])
            access_key = st.text_input("Access Key", type="password", value=settings["s3"]["access_key"])

        with col2:
            region = st.selectbox("Region",
                                  ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
                                  index=["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"].index(
                                      settings["s3"]["region"]))
            secret_key = st.text_input("Secret Key", type="password", value=settings["s3"]["secret_key"])

        if st.form_submit_button("💾 Save S3 Settings", use_container_width=True):
            settings["s3"] = {
                "bucket": bucket,
                "access_key": access_key,
                "secret_key": secret_key,
                "region": region
            }
            st.session_state.app_settings = settings
            st.success("✅ S3 settings saved!")

    # Output Folders
    st.markdown("#### Output Folders")

    with st.form("folder_settings"):
        reports_folder = st.text_input("Reports Folder", value=settings["output"]["reports_folder"])
        logs_folder = st.text_input("Logs Folder", value=settings["output"]["logs_folder"])

        if st.form_submit_button("💾 Save Folder Settings", use_container_width=True):
            settings["output"] = {
                "reports_folder": reports_folder,
                "logs_folder": logs_folder
            }
            # Create folders
            os.makedirs(reports_folder, exist_ok=True)
            os.makedirs(logs_folder, exist_ok=True)

            st.session_state.app_settings = settings
            st.success("✅ Folder settings saved!")

    # Environment Variables Info
    with st.expander("🔍 Environment Variables"):
        st.code("""
# Set these in your .env file or environment:
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET=your-bucket-name
        """)