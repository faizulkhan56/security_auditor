# import subprocess
# import threading
# import re
# import os
# import streamlit as st
# import shlex
# import glob
# import datetime
# from services.s3_handler import get_s3_client
# import json
# import tempfile
#
#
# def run_garak_live(cmd, on_update, s3_bucket=None, aws_access_key=None, aws_secret_key=None):
#     """Run garak command with proper argument handling"""
#
#     # Create temp file for progress tracking
#     progress_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json')
#     progress_file.close()
#
#     def update_progress(progress, status, logs):
#         """Update progress file"""
#         try:
#             with open(progress_file.name, 'w') as f:
#                 json.dump({
#                     'progress': progress,
#                     'status': status,
#                     'logs': logs,
#                     'scanning': True
#                 }, f)
#         except:
#             pass
#
#     # Build the complete command with 'garak' prefix
#     if isinstance(cmd, list):
#         if cmd[0] != 'garak':
#             full_cmd = ['garak'] + cmd
#         else:
#             full_cmd = cmd
#     else:
#         full_cmd = shlex.split(cmd)
#         if full_cmd[0] != 'garak':
#             full_cmd = ['garak'] + full_cmd
#
#     print(f"Executing command: {' '.join(full_cmd)}")
#
#     try:
#         # Set environment to handle Unicode properly on Windows
#         env = os.environ.copy()
#         env['PYTHONIOENCODING'] = 'utf-8'
#
#         process = subprocess.Popen(
#             full_cmd,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.STDOUT,
#             text=True,
#             bufsize=1,
#             universal_newlines=True,
#             env=env,
#             encoding='utf-8',
#             errors='replace'
#         )
#
#         log_lines = []
#         report_files = []
#
#         def reader():
#             try:
#                 for line in iter(process.stdout.readline, ''):
#                     line = line.rstrip('\n\r')
#                     if line:
#                         clean_line = line.encode('ascii', 'ignore').decode('ascii')
#                         log_lines.append(clean_line + '\n')
#                         print(f"GARAK OUTPUT: {clean_line}")
#
#                         # Extract report file paths
#                         if "reporting to" in line.lower():
#                             filename_match = re.search(r'reporting to (.+\.jsonl)', line)
#                             if filename_match:
#                                 report_files.append(filename_match.group(1).strip())
#
#                         # Update progress based on output
#                         progress = 0.3
#                         status = "Running scan..."
#
#                         if "probe init:" in line:
#                             progress = 0.4
#                             status = "Probe initialized"
#                         elif "detector init:" in line:
#                             progress = 0.5
#                             status = "Detector ready"
#                         elif "probe start" in line:
#                             progress = 0.6
#                             status = "Probe started"
#                         elif "connect_tcp.complete" in line:
#                             progress = 0.7
#                             status = "Connected to model"
#                         elif "send_request" in line:
#                             progress = 0.8
#                             status = "Sending requests..."
#
#                         # Update progress file and UI
#                         update_progress(progress, status, ''.join(log_lines))
#                         on_update(''.join(log_lines))
#
#             except Exception as e:
#                 error_msg = f"\nError reading output: {str(e)}\n"
#                 log_lines.append(error_msg)
#                 update_progress(0.0, "Error", ''.join(log_lines))
#                 on_update(''.join(log_lines))
#
#         # Start reader thread
#         print("DEBUG: Starting reader thread")
#         t = threading.Thread(target=reader, daemon=True)
#         t.start()
#
#         # Wait for process to complete
#         return_code = process.wait()
#         t.join(timeout=10)
#
#         # Final updates
#         if return_code == 0:
#             log_lines.append("\n✅ Garak scan completed successfully\n")
#             update_progress(1.0, "Completed", ''.join(log_lines))
#         else:
#             log_lines.append(f"\n❌ Garak scan failed with return code: {return_code}\n")
#             update_progress(0.0, "Failed", ''.join(log_lines))
#
#         on_update(''.join(log_lines))
#
#         # Clean up progress file
#         try:
#             os.unlink(progress_file.name)
#         except:
#             pass
#
#         # Upload files to S3 using your S3 handler
#         if s3_bucket and return_code == 0:
#             try:
#                 print("DEBUG: Starting S3 upload")
#                 s3_client = get_s3_client()
#
#                 # Find all generated files with current timestamp
#                 timestamp = datetime.datetime.now().strftime("%Y%m%d")
#
#                 # Look in garak's default output directory
#                 garak_runs_dir = '/Users/panda/.local/share/garak/garak_runs/'#os.path.expanduser("~/.local/share/garak/garak_runs")
#                 patterns = [
#                     f"{garak_runs_dir}/*{timestamp}*.jsonl",
#                     f"{garak_runs_dir}/*{timestamp}*.html",
#                     f"{garak_runs_dir}/*{timestamp}*.log"
#                 ]
#
#                 all_files = []
#                 for pattern in patterns:
#                     matching_files = glob.glob(pattern)
#                     all_files.extend(matching_files)
#
#                 # Add explicitly found report files
#                 all_files.extend([f for f in report_files if os.path.exists(f)])
#
#                 # Remove duplicates
#                 all_files = list(set(all_files))
#                 print(f"DEBUG: Total files to upload: {len(all_files)}")
#
#                 if all_files:
#                     log_lines.append(f"\n📤 Uploading {len(all_files)} files to S3...\n")
#                     on_update(''.join(log_lines))
#
#                     # Create timestamped folder in S3
#                     s3_folder = f"garak-scans/{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
#
#                     # Upload files
#                     uploaded_files = s3_client.upload_file(tuple(all_files), s3_folder)
#
#                     log_lines.append(f"✅ All files uploaded to S3 bucket: {s3_bucket}\n")
#                     log_lines.append(f"📁 S3 Folder: {s3_folder}\n")
#
#                     for uploaded_file in uploaded_files:
#                         log_lines.append(f"   📄 {uploaded_file}\n")
#
#                     on_update(''.join(log_lines))
#                 else:
#                     log_lines.append("⚠️ No files found to upload\n")
#                     on_update(''.join(log_lines))
#
#             except Exception as e:
#                 error_msg = f"\n❌ S3 upload error: {str(e)}\n"
#                 log_lines.append(error_msg)
#                 print(f"DEBUG: S3 upload error: {str(e)}")
#                 on_update(''.join(log_lines))
#
#     except Exception as e:
#         error_msg = f"❌ Unexpected error: {str(e)}\n"
#         update_progress(0.0, "Failed", error_msg)
#         on_update(error_msg)
#         return error_msg, 1

from garak.cli import main
import os
from services.aws import AwsS3
from services.filter import LogFilter
from pathlib import Path


aws_access_key = os.getenv('AWS_S3_ACCESS_KEY')
aws_secret_key = os.getenv('AWS_S3_SECRET_KEY')

aws_client = AwsS3(aws_access_key, aws_secret_key)
cmd = '--model_type ollama --model_name phi3 --probes xss.MdExfil20230929 --report_prefix ollama.phi3.xss.MdExfil20230929.20250801'




def run_garak_live(cmd):
    main(cmd.split(' '))
    log_filter = LogFilter(aws_client, cmd)
    log_path = '/Users/panda/.local/share/garak/garak_runs/'
    data_path = Path(f'{log_path}/{cmd.split('--report_prefix')[-1].replace('.','/').replace(' ','')+'/'}.report.jsonl')
    data = log_filter.read_log_data(data_path)
    log_filter.filtered_output_data(data)


# # run_garak_live(cmd=cmd)