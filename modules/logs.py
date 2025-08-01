import streamlit as st
import boto3
from datetime import datetime
import json


def show():
    st.markdown("### Log Viewer")

    # Get S3 settings
    s3_settings = st.session_state.get('app_settings', {}).get('s3', {})

    if not all([s3_settings.get('bucket'), s3_settings.get('access_key'), s3_settings.get('secret_key')]):
        st.warning("⚠️ Please configure S3 settings first in the Settings page.")
        return

    try:
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=s3_settings['access_key'],
            aws_secret_access_key=s3_settings['secret_key'],
            region_name=s3_settings.get('region', 'us-east-1')
        )

        # List recent log files
        response = s3_client.list_objects_v2(
            Bucket=s3_settings['bucket'],
            Prefix='garak-logs/',
            MaxKeys=50
        )

        if 'Contents' not in response:
            st.info("📁 No log files found in S3 bucket.")
            return

        # Sort by last modified (newest first)
        log_files = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)

        # File selector
        file_options = {}
        for obj in log_files[:20]:  # Show only last 20 files
            key = obj['Key']
            timestamp = obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
            size = f"{obj['Size'] / 1024:.1f}KB" if obj[
                                                        'Size'] < 1024 * 1024 else f"{obj['Size'] / (1024 * 1024):.1f}MB"
            display_name = f"{timestamp} - {key.split('/')[-1]} ({size})"
            file_options[display_name] = key

        if not file_options:
            st.info("📁 No recent log files found.")
            return

        selected_file = st.selectbox(
            "Select log file:",
            options=list(file_options.keys())
        )

        if selected_file:
            # Download and display file content
            s3_key = file_options[selected_file]

            with st.spinner("📥 Loading log file..."):
                try:
                    response = s3_client.get_object(Bucket=s3_settings['bucket'], Key=s3_key)
                    content = response['Body'].read().decode('utf-8')

                    # Display content in scrollable text area
                    st.text_area(
                        "Log Content:",
                        content,
                        height=600,
                        key="log_content"
                    )

                    # Download button
                    st.download_button(
                        label="💾 Download Log File",
                        data=content,
                        file_name=s3_key.split('/')[-1],
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"❌ Failed to load log file: {str(e)}")

    except Exception as e:
        st.error(f"❌ Failed to connect to S3: {str(e)}")
        st.info("💡 Please check your S3 credentials in Settings.")