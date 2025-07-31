import boto3
import os
from typing import List, Tuple


class AwsS3:
    def __init__(
            self,
            aws_access_key_id: str,
            aws_secret_access_key: str,
            bucket_name: str = 'llm-auditor-reports',
            region_name: str = 'us-east-1'
    ):
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.s3_client = self._init_client()
        self.list_of_file_name: List[str] = []

    def _init_client(self):
        return boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

    def list_files(self) -> List[str]:
        """List all files in the S3 bucket."""
        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
        return [obj['Key'] for obj in response.get('Contents', [])]

    def download_file(self, target_dir: str = 'logs') -> None:
        """Download all `.jsonl` files from the S3 bucket."""
        os.makedirs(target_dir, exist_ok=True)
        self.list_of_file_name = []

        response = self.s3_client.list_objects_v2(Bucket=self.bucket_name)
        for obj in response.get('Contents', []):
            key = obj['Key']
            if key.lower().endswith('.jsonl'):
                filename = os.path.join(target_dir, os.path.basename(key))
                try:
                    self.s3_client.download_file(self.bucket_name, key, filename)
                    self.list_of_file_name.append(filename)
                    print(f"✅ Downloaded: {filename}")
                except Exception as e:
                    print(f"❌ Failed to download {key}: {e}")

    def upload_file(self, local_files: Tuple[str, ...], prefix: str = '') -> None:
        """Upload files to S3 under the given prefix (folder)."""
        for filepath in local_files:
            if not os.path.isfile(filepath):
                print(f"⚠️ Skipping non-existent file: {filepath}")
                continue

            key = os.path.join(prefix, os.path.basename(filepath))
            try:
                self.s3_client.upload_file(filepath, self.bucket_name, key)
                print(f"✅ Uploaded: {filepath} -> s3://{self.bucket_name}/{key}")
            except Exception as e:
                print(f"❌ Upload failed for {filepath}: {e}")

    def __repr__(self):
        return f"<AwsS3 bucket='{self.bucket_name}' region='{self.region_name}'>"


if __name__ == '__main__':
    aws_access_key = os.environ.get('AWS_S3_ACCESS_KEY')
    aws_secret_key = os.environ.get('AWS_S3_SECRET_KEY')

    if not aws_access_key or not aws_secret_key:
        raise EnvironmentError("AWS credentials not set in environment variables.")

    s3 = AwsS3(aws_access_key, aws_secret_key)

    print("📂 Files in bucket:")
    for file in s3.list_files():
        print(" -", file)

    s3.download_file()
    print("📥 Downloaded files:")
    print("\n".join(s3.list_of_file_name))
    s3.upload_file(('logs/snowball.SenatorsFull.report.jsonl',), prefix='test/')
