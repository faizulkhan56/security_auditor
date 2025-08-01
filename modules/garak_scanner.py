import logging

import streamlit as st
from modules.constants import probe_dict
import datetime
import os
import threading
import time
from services.garak_runner import run_garak_live
from services.s3_handler import get_s3_client
import glob


def run_garak_background(cmd_args, model_name):
    """Run garak in background thread using subprocess approach"""

    def garak_worker():
        try:
            print(f"DEBUG: Starting garak worker with command: {cmd_args}")

            # Update initial status
            st.session_state.scan_progress = 0.1
            st.session_state.scan_status = "Running scan..."
            st.session_state.garak_logs = ["🚀 Starting Garak scan...\n"]

            # Get S3 client for upload
            try:
                s3_client = get_s3_client()
                s3_bucket = s3_client.bucket_name
                aws_access_key = s3_client.aws_access_key_id
                aws_secret_key = s3_client.aws_secret_access_key
                print(f"DEBUG: S3 client initialized, bucket: {s3_bucket}")
            except Exception as e:
                print(f"DEBUG: S3 error: {str(e)}")
                st.session_state.garak_logs.append(f"⚠️ S3 upload disabled: {str(e)}\n")
                s3_bucket = None
                aws_access_key = None
                aws_secret_key = None

            # Track total log content
            all_logs = []

            def log_updater(log_content):
                """Update logs in real-time"""
                print(f"DEBUG: Log update received, length: {len(log_content)}")

                # Store in session state as list for better performance
                st.session_state.garak_logs = [log_content]

                # Update progress based on log content
                progress = 0.2  # Default progress
                status = "Running scan..."

                if "scan completed successfully" in log_content.lower():
                    progress = 0.9
                    status = "Scan completed"
                elif "uploading results" in log_content.lower():
                    progress = 0.8
                    status = "Uploading to S3..."
                elif "all files uploaded" in log_content.lower():
                    progress = 1.0
                    status = "Completed"
                elif "error" in log_content.lower() or "failed" in log_content.lower():
                    status = "Error detected"
                elif len(log_content) > 100:  # Some progress if we have substantial output
                    progress = min(0.7, 0.2 + len(log_content) / 10000)  # Progressive increase

                st.session_state.scan_progress = progress
                st.session_state.scan_status = status

            print(f"DEBUG: About to call run_garak_live")

            # Run garak using subprocess approach
            log_output, return_code = run_garak_live(
                cmd_args,
            )
            print(f"DEBUG: run_garak_live starting")
            logging.info('Run garak live')
            print(f"DEBUG: run_garak_live completed")

            # Final status update
            if return_code == 0:
                st.session_state.scan_progress = 1.0
                st.session_state.scan_status = "Completed"
            else:
                st.session_state.scan_status = "Failed"
                if st.session_state.garak_logs:
                    current_logs = st.session_state.garak_logs[0] if st.session_state.garak_logs else ""
                    st.session_state.garak_logs = [current_logs + f"\n❌ Scan failed with exit code: {return_code}\n"]

        except Exception as e:
            print(f"DEBUG: Exception in garak_worker: {str(e)}")
            st.session_state.scan_status = "Failed"
            current_logs = st.session_state.garak_logs[0] if st.session_state.garak_logs else ""
            st.session_state.garak_logs = [current_logs + f"\n❌ Scan failed: {str(e)}\n"]
        finally:
            print("DEBUG: Setting garak_scanning to False")
            st.session_state.garak_scanning = False

    # Start background thread
    print("DEBUG: Starting background thread")
    thread = threading.Thread(target=garak_worker, daemon=True)
    thread.start()

    # Store thread reference
    st.session_state.garak_thread = thread

def build_garak_command(form_data):
    """Build the garak command arguments"""
    cmd_parts = ["--model_type", form_data["model_type"]]

    if form_data["model_name"]:
        cmd_parts += ["--model_name", form_data["model_name"]]

    if form_data["endpoint"]:
        # Add timeout settings for Ollama - increase to 180 seconds
        generator_opts = f'{{"api_base": "{form_data["endpoint"]}", "timeout": 180, "request_timeout": 180}}'
        cmd_parts += ["--generator_options", generator_opts]

    if form_data["probe_secondary"]:
        cmd_parts += ["--probes", ",".join(form_data["probe_secondary"])]

    if form_data["generations"] > 0:
        cmd_parts += ["--generations", str(form_data["generations"])]

    if form_data["parallel_requests"] > 0:
        cmd_parts += ["--parallel_requests", str(form_data["parallel_requests"])]

    if form_data["api_token"]:
        cmd_parts += ["--model_api_key", form_data["api_token"]]

    # Add report prefix with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    probe_names = ".".join([p.split(".")[-1] for p in form_data["probe_secondary"]])
    report_prefix = f"ollama.{form_data['model_name']}.{probe_names}.{timestamp}"
    cmd_parts += ["--report_prefix", report_prefix]
    return cmd_parts

def show():
    # Clean styling
    st.markdown("""
        <style>
        .stTextInput > div > div > input {
            font-size: 14px !important;
            height: 44px !important;
        }
        .stCheckbox > label {
            font-size: 14px !important;
            font-weight: 500 !important;
        }
        .stMultiSelect > div > div {
            font-size: 14px !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # Initialize session state
    if "garak_form_data" not in st.session_state:
        st.session_state.garak_form_data = {
            "model_type": "ollama",
            "model_name": "",
            "endpoint": "",
            "probe_primary": [],
            "probe_secondary": [],
            "generations": 0,
            "parallel_requests": 0,
            "api_token": ""
        }

    if "garak_scanning" not in st.session_state:
        st.session_state.garak_scanning = False
    if "scan_progress" not in st.session_state:
        st.session_state.scan_progress = 0.0
    if "scan_status" not in st.session_state:
        st.session_state.scan_status = "Ready"
    if "garak_logs" not in st.session_state:
        st.session_state.garak_logs = []

    form_data = st.session_state.garak_form_data

    # Show persistent scan status at top if running
    if st.session_state.garak_scanning:
        st.info(f"🔄 Scan in progress: {st.session_state.scan_status} - {st.session_state.scan_progress * 100:.0f}%")

    # Model Configuration
    col1, col2, col3 = st.columns([2, 2, 2])

    with col1:
        model_type = st.text_input(
            "Model Type *",
            value=form_data["model_type"],
            disabled=st.session_state.garak_scanning
        )
        if not st.session_state.garak_scanning:
            form_data["model_type"] = model_type

    with col2:
        model_name = st.text_input(
            "Model Name *",
            value=form_data["model_name"],
            disabled=st.session_state.garak_scanning
        )
        if not st.session_state.garak_scanning:
            form_data["model_name"] = model_name

    with col3:
        endpoint = st.text_input(
            "Endpoint",
            value=form_data["endpoint"],
            disabled=st.session_state.garak_scanning
        )
        if not st.session_state.garak_scanning:
            form_data["endpoint"] = endpoint

    st.markdown("---")

    # Choose Security Categories
    st.markdown("**Choose Security Categories**")

    probe_bases = list(probe_dict.keys())
    selected_primaries = []

    # Grid layout for categories
    cols = st.columns(3)
    for i, probe_base in enumerate(probe_bases):
        with cols[i % 3]:
            if st.checkbox(
                    probe_base,
                    value=probe_base in form_data["probe_primary"],
                    key=f"primary_{probe_base}",
                    disabled=st.session_state.garak_scanning
            ):
                selected_primaries.append(probe_base)

    if not st.session_state.garak_scanning:
        form_data["probe_primary"] = selected_primaries

    # Probe Details selection
    if form_data["probe_primary"]:
        st.markdown("**Probe Details**")

        all_secondary_options = []
        for p in form_data["probe_primary"]:
            for test in probe_dict[p]:
                all_secondary_options.append(f"{p}.{test}")

        selected_secondary = st.multiselect(
            "",
            all_secondary_options,
            default=[x for x in form_data["probe_secondary"] if x in all_secondary_options],
            key="secondary_selection",
            label_visibility="collapsed",
            disabled=st.session_state.garak_scanning
        )

        if not st.session_state.garak_scanning:
            form_data["probe_secondary"] = selected_secondary

    # Advanced Settings
    with st.expander("Advanced Settings"):
        adv_col1, adv_col2 = st.columns(2)

        with adv_col1:
            generations = st.number_input(
                "Generations",
                min_value=0,
                max_value=100,
                value=form_data["generations"],
                key="generations_input",
                disabled=st.session_state.garak_scanning
            )
            if not st.session_state.garak_scanning:
                form_data["generations"] = generations

        with adv_col2:
            parallel_requests = st.number_input(
                "Parallel Requests",
                min_value=0,
                max_value=20,
                value=form_data["parallel_requests"],
                key="parallel_input",
                disabled=st.session_state.garak_scanning
            )
            if not st.session_state.garak_scanning:
                form_data["parallel_requests"] = parallel_requests

        api_token = st.text_input(
            "API Token",
            type="password",
            value=form_data["api_token"],
            key="token_input",
            disabled=st.session_state.garak_scanning
        )
        if not st.session_state.garak_scanning:
            form_data["api_token"] = api_token

    # Command Preview
    with st.expander("Command Preview"):
        if form_data["model_name"] and form_data["probe_secondary"]:
            preview_cmd = build_garak_command(form_data)
            full_preview = ["garak"] + preview_cmd
            st.code(" ".join(full_preview), language="bash")

    # Scan Controls
    can_start = bool(form_data["model_type"] and form_data["model_name"] and form_data["probe_secondary"])

    col1, col2 = st.columns(2)

    with col1:
        if not st.session_state.garak_scanning:
            if st.button("🚀 Start Scan", type="primary", disabled=not can_start, use_container_width=True):
                st.session_state.garak_scanning = True
                st.session_state.scan_progress = 0.0
                st.session_state.scan_status = "Initializing..."
                st.session_state.garak_logs = []

                # Build and start scan in background
                final_cmd = build_garak_command(form_data)
                run_garak_background(final_cmd, form_data["model_name"])

                st.rerun()

    with col2:
        if st.session_state.garak_scanning:
            if st.button("❌ Cancel Scan", type="secondary", use_container_width=True):
                st.session_state.garak_scanning = False
                st.session_state.scan_progress = 0.0
                st.session_state.scan_status = "Cancelled"
                st.rerun()

    # Show scan progress and logs
    if st.session_state.garak_scanning or st.session_state.garak_logs:
        st.markdown("---")

        # Show scan progress and logs
        if st.session_state.garak_scanning or st.session_state.garak_logs:
            st.markdown("---")

            # Progress bar
            if st.session_state.garak_scanning:
                progress_bar = st.progress(st.session_state.scan_progress)
                st.text(f"Status: {st.session_state.scan_status}")

                # Check if scan completed by looking for report files
                if st.session_state.scan_status == "Running scan...":
                    # Look for garak report files to update progress
                    report_pattern = f"*{datetime.datetime.now().strftime('%Y%m%d')}*.jsonl"
                    report_files = glob.glob(os.path.expanduser(f"~/.local/share/garak/garak_runs/{report_pattern}"))

                    if report_files:
                        st.session_state.scan_progress = 0.8
                        st.session_state.scan_status = "Generating reports..."

                # Auto-refresh every 3 seconds
                time.sleep(3)
                st.rerun()

            # Show logs
            if st.session_state.garak_logs:
                st.markdown("**Scan Logs**")
                log_content = "".join(st.session_state.garak_logs)
                st.text_area("📋 Garak Logs", log_content, height=400, key="persistent_logs")

            # Show completion status
            if not st.session_state.garak_scanning and st.session_state.garak_logs:
                if st.session_state.scan_status == "Completed":
                    st.success("✅ Scan and upload completed successfully!")
                elif st.session_state.scan_status == "Failed":
                    st.error("❌ Scan failed. Check logs for details.")
                elif st.session_state.scan_status == "Cancelled":
                    st.warning("⚠️ Scan was cancelled.")
    # Update session state
    st.session_state.garak_form_data = form_data