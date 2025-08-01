import boto3
import os
from typing import List, Tuple
from dotenv import load_dotenv


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

    def upload_file(self, local_files: Tuple[str, ...], prefix: str = '') -> List[str]:
        """Upload files to S3 under the given prefix (folder)."""
        uploaded_files = []
        for filepath in local_files:
            if not os.path.isfile(filepath):
                print(f"⚠️ Skipping non-existent file: {filepath}")
                continue

            key = os.path.join(prefix, os.path.basename(filepath)).replace('\\', '/')
            try:
                self.s3_client.upload_file(filepath, self.bucket_name, key)
                s3_url = f"s3://{self.bucket_name}/{key}"
                uploaded_files.append(s3_url)
                print(f"✅ Uploaded: {filepath} -> {s3_url}")
            except Exception as e:
                print(f"❌ Upload failed for {filepath}: {e}")

        return uploaded_files


def get_s3_client():
    """Get S3 client from environment variables with explicit .env loading"""

    # Find and load .env file from project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)  # Go up one level from services/
    env_path = os.path.join(project_root, '.env')

    print(f"DEBUG: Loading .env from: {env_path}")
    print(f"DEBUG: .env exists: {os.path.exists(env_path)}")

    # Force load with override=True to override system env vars
    load_dotenv(env_path, override=True)

    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.getenv('S3_BUCKET', 'llm-auditor-reports')
    region = os.getenv('AWS_REGION', 'us-east-1')

    print(f"DEBUG: Loaded AWS_ACCESS_KEY_ID: {aws_access_key[:12] if aws_access_key else 'None'}...")
    print(f"DEBUG: Loaded S3_BUCKET: {bucket_name}")

    if not aws_access_key or not aws_secret_key:
        raise EnvironmentError(
            f"AWS credentials not set. Found key: {aws_access_key[:8] if aws_access_key else 'None'}")

    return AwsS3(aws_access_key, aws_secret_key, bucket_name, region)