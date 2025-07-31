import sys
import io
from garak.cli import main

def run_garak_streamlit():
    # Prepare argument list
    CMD = "--model_type ollama --model_name phi3 --probes dan.AntiDAN --report_prefix dan.AntiDAN"
    args = CMD.split()

    # Replace sys.stdout with a StringIO buffer
    buffer = io.StringIO()
    sys_stdout = sys.stdout
    sys.stderr = sys.stderr

    sys.stdout = buffer
    sys.stderr = buffer

    output_placeholder = st.empty()

    try:
        # Run garak main directly
        main(CMD.split(' '))
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        sys.stdout = sys_stdout
        sys.stderr = sys.stderr

    # Stream output to Streamlit
    buffer.seek(0)
    output = buffer.read()
    output_placeholder.text_area("📋 Garak Logs", output, height=500)


import streamlit as st

st.title("🔍 Garak Model Stream")

if st.button("Run DAN Probe"):
    with st.spinner("Running Garak..."):
        run_garak_streamlit()
