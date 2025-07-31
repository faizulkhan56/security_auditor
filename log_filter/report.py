import streamlit as st
import pandas as pd
import json
import datetime
import plotly.express as px

# === Input data (copy from your actual report or load JSON file) ===
data = {
    7: {
        "reportfile": "latentinjection.LatentInjectionReport.report.jsonl",
        "garak_version": "0.12.0.pre1",
        "start_time": "2025-07-31T12:35:19.768746",
        "run_uuid": "53f17a8b-614c-47ae-9011-a61c3834c6af",
        "setup": {
            "system.parallel_requests": 10,
            "system.parallel_attempts": 10,
            "run.soft_probe_prompt_cap": 1,
            "run.generations": 1,
            "plugins.model_type": "ollama",
            "plugins.model_name": "phi3",
            "plugins.probe_spec": "latentinjection.LatentInjectionReport",
            "reporting.report_prefix": "latentinjection.LatentInjectionReport",
        },
        "model_type": "ollama",
        "model_name": "phi3",
        "group_aggregation_function": "lower_quartile",
        "report_digest_time": "2025-07-31T12:35:50.252953",
        "calibration_used": True,
        "calibration": {
            "calibration_date": "2025-05-28 22:03:12.471875+00:00Z",
            "model_count": 23,
        }
    }
}

# === Extract relevant info ===
report = data[7]
setup = report["setup"]
start_time = pd.to_datetime(report["start_time"])
end_time = pd.to_datetime(report["report_digest_time"])
duration = end_time - start_time

# === Streamlit Dashboard ===
st.set_page_config(page_title="Garak Run Report", layout="wide")
st.title("🛡️ Garak Vulnerability Scan Report")

# --- Overview ---
st.header("🔍 Scan Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Model", f"{report['model_type']} / {report['model_name']}")
col2.metric("Probe", setup['plugins.probe_spec'])
col3.metric("Runtime", str(duration))

# --- System Setup ---
st.subheader("⚙️ System Parameters")
st.json({
    "Parallel Requests": setup["system.parallel_requests"],
    "Parallel Attempts": setup["system.parallel_attempts"],
    "Prompt Cap": setup["run.soft_probe_prompt_cap"],
    "Generations": setup["run.generations"],
    "UUID": report["run_uuid"],
})

# --- Calibration Info ---
if report.get("calibration_used"):
    st.subheader("📏 Calibration Info")
    st.info(f"Used calibration from `{report['calibration']['calibration_date']}` with {report['calibration']['model_count']} models.")

# --- Timeline ---
st.subheader("📈 Timeline")
df_time = pd.DataFrame({
    "Event": ["Start", "End"],
    "Timestamp": [start_time, end_time]
})
fig = px.line(df_time, x="Timestamp", y="Event", markers=True, title="Scan Start → End")
st.plotly_chart(fig, use_container_width=True)

# --- Report Output Path ---
st.subheader("📝 Report File")
st.code(report["reportfile"], language="bash")
