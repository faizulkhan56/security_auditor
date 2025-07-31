from datetime import datetime
from log_filter.aws import AwsS3
from pydantic import BaseModel
from typing import Optional


class LogFilterAttributes(BaseModel):
    model_type: Optional[str] = None
    model_name: Optional[str] = None
    execution_day = datetime.now().strftime('%Y%m%d')

    @property
    def folder_prefix(self) -> str:
        return f"{self.model_type}/{self.model_name}/{self.execution_day}/"


class LogFilter:
    def __init__(self, aws_client: AwsS3) -> None:
        self.aws_client = aws_client

    def read_data(self):
        pass

    def filtered_output_write_file(self):
        pass
