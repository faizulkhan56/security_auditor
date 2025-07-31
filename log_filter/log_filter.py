from datetime import datetime
from aws import AwsS3
from pydantic import BaseModel, Field
import pandas as pd
import logging


# class LogFilterAttributes(BaseModel):
#     model_type: str | None = None
#     model_name: str | None = None
#     execution_date = Field(default_factory=lambda: datetime.now().strftime('%Y%m%d'))
#
#
#     @property
#     def folder_prefix(self) -> str:
#         return f"{self.model_type}/{self.model_name}/{self.execution_date}/"


class LogFilter:
    def __init__(self, aws_client: AwsS3) -> None:
        self.aws_client = aws_client

    @staticmethod
    def read_log_data(file_name: str) -> pd.DataFrame:
        df = pd.read_json(file_name, lines=True)
        return df

    @staticmethod
    def filtered_output_data(df: pd.DataFrame) -> pd.DataFrame:
        if df[(df.entry_type == 'digest')].shape[0] > 0:
            df_digest_meta = df[(df.entry_type == 'digest')]['meta']
            df_digest_eval = df[(df.entry_type == 'digest')]['eval']
            print(df_digest_meta, df_digest_eval,)
        else:
            logging.info(f"No digest")
        return df


if __name__ == '__main__':
    import os
    aws_access_key = os.environ.get('AWS_S3_ACCESS_KEY')
    aws_secret_key = os.environ.get('AWS_S3_SECRET_KEY')
    aws_client = AwsS3(aws_access_key, aws_secret_key)
    log_filter = LogFilter(aws_client)
    data = log_filter.read_log_data('/Users/panda/Desktop/Hackathon/security_auditor/logs/ansiescape.AnsiEscaped.report.jsonl')
    log_filter.filtered_output_data(data)