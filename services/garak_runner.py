from garak.cli import main
import os
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
cmd = '--model_type ollama --model_name phi3 --probes dan.DAN_Jailbreak --generations 1 --report_prefix ollama.phi3.DAN_Jailbreak.20250801'


def run_garak_live(cmd, on_update=None):
    """
    Run garak with real-time output capture for garak_scanner.py
    Args:
        cmd: Command string to run
        on_update: Callback function to receive real-time updates
    """
    print(f"DEBUG: Starting garak with command: {cmd}")

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
        import subprocess
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
                log_output += line
                print(f"DEBUG: Garak output: {line.strip()}")

        # Wait for process to complete
        return_code = process.wait()
        print(f"DEBUG: Garak process completed with return code: {return_code}")

        # Process the results using the original logic
        try:
            log_filter = LogFilter(aws_client, cmd)
            log_path = f"{os.getenv('LOG_PATH', '~')}.local/share/garak/garak_runs/"
            print(f"DEBUG: Log path: {log_path}")
            # Extract report prefix from command
            cmd_parts = cmd.split()
            report_prefix = None
            for i, part in enumerate(cmd_parts):
                if part == '--report_prefix' and i + 1 < len(cmd_parts):
                    report_prefix = cmd_parts[i + 1]
                    break

            if report_prefix:
                # Fix the path to use the correct user directory
                user_home = os.path.expanduser("~")
                data_path = Path(f"{user_home}/.local/share/garak/garak_runs/{report_prefix}.report.jsonl")
                print(f"DEBUG: Looking for report file: {data_path}")

                if data_path.exists():
                    data = log_filter.read_log_data(data_path)
                    filtered_df = log_filter.filtered_output_data(data)
                    response_data = report_generator.generate_report_from_openai(df=filtered_df)
                    return log_output, return_code, response_data
                else:
                    print(f"DEBUG: Report file not found: {data_path}")
            else:
                print("DEBUG: No report prefix found in command")

        except Exception as e:
            print(f"DEBUG: Error processing results: {e}")

        return log_output, return_code, None

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
    response_data = run_garak_live(cmd)
    save_report(response_data, cmd)

