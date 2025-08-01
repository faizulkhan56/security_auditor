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


def run_garak_live(cmd):
    main(cmd.split(' '))
    log_filter = LogFilter(aws_client, cmd)
    log_path = f"{os.getenv('LOG_PATH')}.local/share/garak/garak_runs/"
    data_path = Path(f"{log_path}/{cmd.split('--report_prefix')[-1].strip()}.report.jsonl")
    data = log_filter.read_log_data(data_path)
    filtered_df = log_filter.filtered_output_data(data)
    response_data = report_generator.generate_report_from_openai(df=filtered_df)
    return response_data


def save_report(response_data):
    report_path = f"{os.getenv('REPORT_PATH')}.local/share/garak/reports"
    Path(report_path).mkdir(parents=True, exist_ok=True)
    report_file = f"{report_path}/{cmd.split('--report_prefix')[-1].strip()}.report.json"

    # Ensure the report file is saved in JSON format
    with open(report_file, 'w', encoding='utf-8') as file:
        if isinstance(response_data, pd.DataFrame):
            response_data = response_data.to_json(orient='records', indent=2)
        file.write(response_data)

    print(f"Report saved to {report_file}")


def clean_up_reports(report_file):
    """
    Clean up old reports from the local directory, keeping only the specified report.
    """
    report_path = f"{os.getenv('REPORT_PATH')}.local/share/garak/reports"
    Path(report_path).mkdir(parents=True, exist_ok=True)

    # Extract timestamp from the report_file parameter
    keep_file = Path(report_file).name

    for file in Path(report_path).glob('*.report.*.json'):
        if file.name != keep_file:
            file.unlink(missing_ok=True)
            print(f"Deleted old report: {file.name}")
        else:
            print(f"Kept report: {file.name}")


if __name__ == "__main__":
    response_data = run_garak_live(cmd)
    save_report(response_data)
