import logging
import streamlit as st
from modules.constants import probe_dict
import datetime
import os
import time
from services.garak_runner import run_garak_live
import glob
import threading
import subprocess
from streamlit.runtime.scriptrunner import add_script_run_ctx
import queue

# Global queue for log updates
log_queue = queue.Queue()


def get_latest_logs():
    """Get the latest logs from the queue"""
    latest_logs = ""
    try:
        while not log_queue.empty():
            latest_logs = log_queue.get_nowait()
    except queue.Empty:
        pass
    return latest_logs


def run_garak_live_with_updates(cmd):
    """
    Run garak with real-time output capture and Streamlit updates
    """
    print(f"DEBUG: Starting garak with real-time updates: {cmd}")

    # Build the full command
    full_cmd = ["garak"] + cmd.split()
    print(f"DEBUG: Full command: {' '.join(full_cmd)}")

    # Set environment for proper output handling
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    env['FORCE_COLOR'] = '0'  # Disable color output for better parsing

    log_output = ""

    try:
        # Start the process
        process = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0,  # Unbuffered
            universal_newlines=True,
            env=env,
            encoding='utf-8',
            errors='replace'
        )

        # Read output in real-time
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break

            if line:
                # Clean the line
                clean_line = line.encode('ascii', errors='ignore').decode('ascii')
                log_output += clean_line

                # Put log update in queue for real-time display
                try:
                    log_queue.put_nowait(log_output)
                except queue.Full:
                    pass  # Queue is full, skip this update

                # Note: Progress updates removed to avoid ScriptRunContext warnings
                # Progress will be updated by the main thread based on log content

                print(f"DEBUG: Garak output: {clean_line.strip()}")

        # Wait for process to complete
        return_code = process.wait()
        print(f"DEBUG: Garak process completed with return code: {return_code}")
        run_garak_live(cmd, on_update=None)
        return log_output, return_code, None

    except Exception as e:
        print(f"DEBUG: Error starting garak process: {e}")
        error_msg = f"Error starting garak: {str(e)}"
        return error_msg, -1, None


def run_garak_background(cmd_args, model_name):
    """Run garak in background thread using subprocess approach"""

    def garak_worker():
        try:
            print(f"DEBUG: Starting garak worker with command: {' '.join(cmd_args)}")

            # Run garak using subprocess approach with real-time updates
            log_output, return_code, response_data = run_garak_live_with_updates(
                ' '.join(cmd_args)
            )

            print(f"DEBUG: run_garak_live completed")

            # Final status update - use queue instead of direct session state access
            if return_code == 0:
                final_status = "Completed"
                final_message = f"\nScan completed successfully!\n"
            else:
                final_status = "Failed"
                final_message = f"\nScan failed with exit code: {return_code}\n"

            # Put final status in queue for main thread to process
            try:
                log_queue.put_nowait(log_output + final_message)
            except queue.Full:
                pass



        except Exception as e:
            print(f"DEBUG: Exception in garak_worker: {str(e)}")
            error_message = f"\nScan failed: {str(e)}\n"
            try:
                log_queue.put_nowait(error_message)
            except queue.Full:
                pass
        finally:
            print("DEBUG: Setting garak_scanning to False")
            # Use a simple flag instead of session state
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
    if form_data["probe_secondary"]:
        probe_names = ".".join([p.split(".")[-1] for p in form_data["probe_secondary"]])
        report_prefix = f"ollama.{form_data['model_name']}.{probe_names}.{timestamp}"
    else:
        report_prefix = f"ollama.{form_data['model_name']}.scan.{timestamp}"
    cmd_parts += ["--report_prefix", report_prefix]

    print(f"DEBUG: Built command: {cmd_parts}")
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
    if "last_log_update" not in st.session_state:
        st.session_state.last_log_update = None

    form_data = st.session_state.garak_form_data

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
            "Select Probes",
            all_secondary_options,
            default=[x for x in form_data["probe_secondary"] if x in all_secondary_options],
            key="secondary_selection",
            disabled=st.session_state.garak_scanning,
            label_visibility="visible"
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
            # Show "Refresh" if there are existing logs, otherwise "Start Scan"
            button_text = "🔄 Refresh" if st.session_state.garak_logs else "🚀 Start Scan"
            if st.button(button_text, type="primary", disabled=not can_start, use_container_width=True):
                print(f"DEBUG: Start scan button clicked")
                print(f"DEBUG: Form data: {form_data}")

                st.session_state.garak_scanning = True
                st.session_state.scan_progress = 0.1
                st.session_state.scan_status = "Starting scan..."
                st.session_state.garak_logs = ["Starting Garak scan...\n"]
                st.session_state.last_log_update = datetime.datetime.now().strftime("%H:%M:%S")

                # Build and start scan in background
                final_cmd = build_garak_command(form_data)
                print(f"DEBUG: Final command: {final_cmd}")
                run_garak_background(final_cmd, form_data["model_name"])

                st.rerun()

    with col2:
        if st.session_state.garak_scanning:
            if st.button("❌ Cancel Scan", type="secondary", use_container_width=True):
                st.session_state.garak_scanning = False
                st.session_state.scan_progress = 0.0
                st.session_state.scan_status = "Cancelled"
                st.rerun()

    # Check for new logs from queue when scanning
    if st.session_state.get('garak_scanning', False):
        latest_logs = get_latest_logs()
        if latest_logs:
            st.session_state.garak_logs = [latest_logs]
            st.session_state.last_log_update = datetime.datetime.now().strftime("%H:%M:%S")

    # Show logs
    if st.session_state.garak_scanning or st.session_state.garak_logs:
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.session_state.last_log_update:
                st.caption(f"Last update: {st.session_state.last_log_update}")
        with col2:
            if st.button("🔄", help="Refresh logs", key="refresh_logs_icon", use_container_width=True):
                st.rerun()

        log_content = st.session_state.garak_logs[0] if st.session_state.garak_logs else ""

        # Clean the log content - remove ANSI codes and artifacts
        def clean_log_content(content):
            import re

            # Remove ANSI escape codes (color codes, formatting, etc.)
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            content = ansi_escape.sub('', content)

            # Remove other common escape sequences
            content = re.sub(r'\[[0-9;]*[a-zA-Z]', '', content)
            content = re.sub(r'\[[0-9;]*m', '', content)

            lines = content.split('\n')
            cleaned_lines = []
            for line in lines:
                # Remove lines that are just "|" or blank spaces
                cleaned_line = line.strip()
                if cleaned_line and cleaned_line != "|" and not cleaned_line.isspace():
                    # Remove lines containing file paths and directory information
                    if not any(path_indicator in cleaned_line.lower() for path_indicator in [
                        'logging to ', 'reporting to ', 'report closed', 'report html summary',
                        'c:\\', 'c:/', '/users/', '\\users\\', '.jsonl', '.html', '.log'
                    ]):
                        cleaned_lines.append(cleaned_line)
            return '\n'.join(cleaned_lines)

        # Clean and split logs into lines
        cleaned_content = clean_log_content(log_content)
        log_lines = cleaned_content.split('\n')
        if len(log_lines) > 50:
            display_logs = '\n'.join(log_lines[-50:])
            st.info(f"Showing last 50 lines of {len(log_lines)} total lines")
        else:
            display_logs = cleaned_content

        st.text_area("📋 Garak Logs", display_logs, height=400, key="persistent_logs")

        # Show simple completion status
        if not st.session_state.garak_scanning and st.session_state.garak_logs:
            if "garak run complete" in st.session_state.garak_logs[0].lower():
                st.success("Scan completed!")
            elif "cancelled" in st.session_state.scan_status.lower():
                st.warning("Scan was cancelled.")

    # Update session state
    st.session_state.garak_form_data = form_data