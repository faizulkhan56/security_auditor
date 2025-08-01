import streamlit as st
from services.promptfoo_runner import run_promptfoo_live


def show():
    st.subheader("Promptfoo Scanner")
    st.info("Run prompt evaluation suites with Promptfoo. Make sure promptfoo is installed.")

    pf_model = st.text_input("Model name or endpoint for Promptfoo", key="promptfoo_model")
    pf_suite = st.text_input("Path to promptfoo test suite YAML", key="promptfoo_suite")

    output_placeholder = st.empty()

    if st.button("Run Promptfoo Scan", type="primary"):
        cmd = ["promptfoo", "test", pf_suite, "--provider", pf_model]

        def on_update(text):
            output_placeholder.text_area("Promptfoo Output", text, height=400)

        with st.spinner("Running Promptfoo scan..."):
            logs, code = run_promptfoo_live(cmd, on_update)
            output_placeholder.text_area("Promptfoo Scan Finished. Output:", logs, height=400)