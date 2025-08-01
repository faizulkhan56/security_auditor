import os
import sys
from dotenv import load_dotenv

# Add parent directory to path so we can import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Force load .env from project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, '.env')

print(f"Loading .env from: {env_path}")
print(f".env exists: {os.path.exists(env_path)}")

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        print("Contents of .env:")
        for line in f:
            if 'AWS_ACCESS_KEY_ID' in line:
                print(f"   {line.strip()}")

load_dotenv(env_path, override=True)

print(f"After loading - AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID')}")

from services.s3_handler import get_s3_client

try:
    s3_client = get_s3_client()
    print(f"✅ Connected to bucket: {s3_client.bucket_name}")
    print(f"🔑 Using Access Key: {s3_client.aws_access_key_id[:12]}...")

    # Test bucket access
    print("\n🧪 Testing bucket access...")
    response = s3_client.s3_client.list_objects_v2(Bucket=s3_client.bucket_name)

    if 'Contents' in response:
        print(f"📁 Found {len(response['Contents'])} files")
        for obj in response['Contents'][:3]:
            print(f"   📄 {obj['Key']}")
    else:
        print("📭 Bucket is empty")

except Exception as e:
    print(f"❌ Error: {e}")