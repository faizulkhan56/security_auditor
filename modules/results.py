# import streamlit as st
# import os
#
# def show():
#     st.header("Scan Results & Logs")
#     op_log_path = st.text_input("Operational Log Folder", "C:/Users/Cefalo/.local/share/garak", key="op_log_path")
#     scan_log_path = st.text_input("Scan Log Folder", "C:/Users/Cefalo/.local/share/garak/garak_runs", key="scan_log_path")
#     tab1, tab2 = st.tabs(["Operational Log", "Scan Output"])
#
#     with tab1:
#         st.subheader("Operational Log")
#         if st.button("Refresh Operational Log"):
#             st.experimental_rerun()
#         if os.path.exists(op_log_path):
#             files = [f for f in os.listdir(op_log_path) if f.endswith(".log") or f.endswith(".txt")]
#             if not files:
#                 st.write("No logs found in folder.")
#             else:
#                 selected = st.selectbox("Choose log file", files, key="op_log_file")
#                 with open(os.path.join(op_log_path, selected), "r", encoding="utf8", errors="ignore") as f:
#                     log_text = f.read()
#                 st.text_area("Operational Log Content", log_text, height=400)
#                 st.download_button("Download Log", log_text, file_name=selected)
#         else:
#             st.error("Log folder not found.")
#
#     with tab2:
#         st.subheader("Scan Output Log")
#         if st.button("Refresh Scan Output"):
#             st.experimental_rerun()
#         if os.path.exists(scan_log_path):
#             files = [f for f in os.listdir(scan_log_path) if f.endswith(".log") or f.endswith(".txt") or f.endswith(".jsonl")]
#             if not files:
#                 st.write("No scan output logs found in folder.")
#             else:
#                 selected = st.selectbox("Choose scan output file", files, key="scan_log_file")
#                 with open(os.path.join(scan_log_path, selected), "r", encoding="utf8", errors="ignore") as f:
#                     log_text = f.read()
#                 st.text_area("Scan Output Log Content", log_text, height=400)
#                 st.download_button("Download Scan Output", log_text, file_name=selected)
#         else:
#             st.error("Scan output folder not found.")
