import logging
import os
from pathlib import Path

import pandas as pd
from aws import AwsS3


class LogFilter:
    def __init__(self, aws_client: AwsS3, cmd: str) -> None:
        self.aws_client = aws_client
        self.cmd = cmd.strip()
        try:
            prefix = cmd.split('--report_prefix')[-1].strip().replace('.', '/')
            self.folder_prefix = prefix if prefix.endswith('/') else prefix + '/'
            self.report_name = cmd.split('--report_prefix')[-1].strip()
        except IndexError:
            raise ValueError("Missing '--report_prefix' in cmd")

    def read_log_data(self, file_name: str) -> pd.DataFrame:
        try:
            return pd.read_json(file_name, lines=True)
        except Exception as e:
            logging.error(f"Failed to read JSON log file: {file_name}, error: {e}")
            raise

    def filtered_output_data(self, df: pd.DataFrame, target_dir: str = 'filtered_logs/') -> pd.DataFrame:
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        if df['entry_type'].eq('digest').any():
            filtered_df = df.query("entry_type in ['digest', 'attempt']")
            filtered_df = filtered_df[filtered_df['detector_results'].map(bool)]
            output_path = f"{target_dir}{self.report_name}.report.jsonl"
            filtered_df.to_json(output_path, orient='records', lines=True)
            logging.info(f"Filtered report saved to: {output_path}")
            self.aws_client.upload_file(local_files=(output_path,), prefix=self.folder_prefix)
        else:
            logging.info("No digest entries found.")

        return df


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    aws_access_key = os.getenv('AWS_S3_ACCESS_KEY')
    aws_secret_key = os.getenv('AWS_S3_SECRET_KEY')

    aws_client = AwsS3(aws_access_key, aws_secret_key)
    cmd = '--model_type ollama --model_name phi3 --probes dan.AntiDAN --report_prefix ollama.phi3.dan.AntiDAN.20250801'

    log_filter = LogFilter(aws_client, cmd)

    data_path = Path('logs/ansiescape.AnsiEscaped.report.jsonl')
    data = log_filter.read_log_data(data_path)
    log_filter.filtered_output_data(data)
