from garak.cli import main
import os
from aws import AwsS3
from open_api_communication import OpenApiCommunication
from report_generate import ReportGenerate
from filter import LogFilter
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
    log_path = f'{os.getenv('LOG_PATH')}.local/share/garak/garak_runs/'
    data_path = Path(f'{log_path}/{cmd.split('--report_prefix')[-1].strip()}.report.jsonl')
    data = log_filter.read_log_data(data_path)
    filtered_df = log_filter.filtered_output_data(data)
    response_data = report_generator.generate_report_from_openai(df=filtered_df)
    print(response_data)


run_garak_live(cmd=cmd)