from garak.cli import main
import subprocess
import threading
import os
from aws import AwsS3
from filter import LogFilter
from pathlib import Path


aws_access_key = os.getenv('AWS_S3_ACCESS_KEY')
aws_secret_key = os.getenv('AWS_S3_SECRET_KEY')

aws_client = AwsS3(aws_access_key, aws_secret_key)
cmd = '--model_type ollama --model_name phi3 --probes xss.MdExfil20230929 --report_prefix ollama.phi3.xss.MdExfil20230929.20250801'




def run_garak_live(cmd):
    main(cmd.split(' '))
    log_filter = LogFilter(aws_client, cmd)
    log_path = '/Users/panda/.local/share/garak/garak_runs/'
    data_path = Path(f'{log_path}/ollama.phi3.xss.MdExfil20230929.20250801.report.jsonl')
    data = log_filter.read_log_data(data_path)
    log_filter.filtered_output_data(data)


run_garak_live(cmd=cmd)