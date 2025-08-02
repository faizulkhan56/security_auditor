import subprocess
import threading
import os
import tempfile
from services.aws import AwsS3
from services.open_api_communication import OpenApiCommunication
from services.report_generate import ReportGenerate
from services.filter import LogFilter
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

aws_access_key = os.getenv('AWS_S3_ACCESS_KEY')
aws_secret_key = os.getenv('AWS_S3_SECRET_KEY')

aws_client = AwsS3(aws_access_key, aws_secret_key)
openapi_communication = OpenApiCommunication()
report_generator = ReportGenerate(openapi_communication)


def run_garak_live(cmd, on_update=None):
    """
    Run garak with real-time output capture
    Args:
        cmd: Command string to run
        on_update: Callback function to receive real-time updates
    """
    print(f"DEBUG: Starting garak with command: {cmd}")

    # Create a temporary file for logs
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.log') as log_file:
        log_file_path = log_file.name

    # Build the full command
    full_cmd = ["garak"] + cmd.split()
    print(f"DEBUG: Full command: {' '.join(full_cmd)}")

    # Set environment for proper output handling
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    env['FORCE_COLOR'] = '0'  # Disable color output for better parsing

    # Start the process
    try:
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

        def reader():
            """Read output and write to file"""
            try:
                with open(log_file_path, 'w', encoding='utf-8') as f:
                    while True:
                        line = process.stdout.readline()
                        if not line:
                            break

                        # Clean the line
                        clean_line = line.encode('ascii', errors='ignore').decode('ascii')
                        f.write(clean_line)
                        f.flush()  # Force write to disk

                        # Clean print output for terminal
                        clean_print = clean_line.strip().encode('ascii', errors='ignore').decode('ascii')
                        print(f"DEBUG: Garak output: {clean_print}")

            except Exception as e:
                print(f"DEBUG: Error reading output: {e}")
            finally:
                if process.stdout:
                    process.stdout.close()

        # Start reader thread
        reader_thread = threading.Thread(target=reader, daemon=True)
        reader_thread.start()

        # Wait for process to complete
        return_code = process.wait()
        reader_thread.join(timeout=10)  # Wait up to 10 seconds for thread to finish

        print(f"DEBUG: Garak process completed with return code: {return_code}")

        # Read the log file
        try:
            with open(log_file_path, 'r', encoding='utf-8') as f:
                log_output = f.read()
        except Exception as e:
            print(f"DEBUG: Error reading log file: {e}")
            log_output = ""

        # Clean up the log file
        try:
            os.unlink(log_file_path)
        except:
            pass

        # Process the results
        log_filter = LogFilter(aws_client, cmd)
        log_path = f"{os.getenv('LOG_PATH')}.local/share/garak/garak_runs/"
        data_path = Path(f"{log_path}/{cmd.split('--report_prefix')[-1].strip()}.report.jsonl")
        data = log_filter.read_log_data(data_path)
        filtered_df = log_filter.filtered_output_data(data)
        response_data = report_generator.generate_report_from_openai(df=filtered_df)
        print(response_data)
        return response_data

    except Exception as e:
        print(f"DEBUG: Error starting garak process: {e}")
        return f"Error starting garak: {str(e)}", -1, None


def save_report(response_data, cmd):
    """Save report to file"""
    try:
        report_path = f"{os.getenv('REPORT_PATH', '~')}.local/share/garak/reports"
        Path(report_path).mkdir(parents=True, exist_ok=True)

        # Extract report prefix from command
        cmd_parts = cmd.split()
        report_prefix = None
        for i, part in enumerate(cmd_parts):
            if part == '--report_prefix' and i + 1 < len(cmd_parts):
                report_prefix = cmd_parts[i + 1]
                break

        if report_prefix:
            report_file = f"{report_path}/{report_prefix}.report.json"

            # Ensure the report file is saved in JSON format
            with open(report_file, 'w', encoding='utf-8') as file:
                if isinstance(response_data, pd.DataFrame):
                    response_data = response_data.to_json(orient='records', indent=2)
                file.write(response_data)

            print(f"Report saved to {report_file}")
        else:
            print("No report prefix found in command")

    except Exception as e:
        print(f"Error saving report: {e}")


def clean_up_reports(report_file):
    """
    Clean up old reports from the local directory, keeping only the specified report.
    """
    try:
        report_path = f"{os.getenv('REPORT_PATH', '~')}.local/share/garak/reports"
        Path(report_path).mkdir(parents=True, exist_ok=True)

        # Extract timestamp from the report_file parameter
        keep_file = Path(report_file).name

        for file in Path(report_path).glob('*.report.*.json'):
            if file.name != keep_file:
                file.unlink(missing_ok=True)
                print(f"Deleted old report: {file.name}")
            else:
                print(f"Kept report: {file.name}")
    except Exception as e:
        print(f"Error cleaning up reports: {e}")


if __name__ == "__main__":
    cmd = '--model_type ollama --model_name phi3 --probes dan.DAN_Jailbreak --generations 1 --report_prefix ollama.phi3.DAN_Jailbreak.20250801'
    log_output, return_code, response_data = run_garak_live(cmd)
    if response_data:
        save_report(response_data, cmd)

