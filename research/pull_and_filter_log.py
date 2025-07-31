import boto3
import pandas as pd
from pprint import pprint


class LogAnalysis:
    def __init__(self, aws_access_key, aws_secret_key, bucket_name, region_name='us-east-1'):
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.s3_client = None
        self.list_of_file_name = []

    def create_client(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
            region_name=self.region_name
        )

    def pull_log_and_write(self):
        """Download the log file from S3 and save it locally."""
        if not self.s3_client:
            raise Exception("S3 client not initialized. Call create_client() first.")

        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
        for obj in response.get('Contents', []):
            local_filename = 'logs/' + obj['Key'].split('/')[-1]
            if '.jsonl' in local_filename:
                self.s3_client.download_file(self.bucket_name, obj['Key'], local_filename)
                self.list_of_file_name.append(local_filename)

    def filter_log(self):
        for file in self.list_of_file_name:
            df = pd.read_json(file, lines=True)



    def upload_to_s3(self, local_path, target_s3_key):
        """Upload a file back to S3."""
        if not self.s3_client:
            raise Exception("S3 client not initialized. Call create_client() first.")

        self.s3_client.upload_file(local_path, self.bucket_name, target_s3_key)
        print(f"Uploaded {local_path} to s3://{self.bucket_name}/{target_s3_key}")


if __name__ == "__main__":
    pass

