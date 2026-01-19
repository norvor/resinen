import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile
import uuid
import json
import os

from app.core.config import settings

# --- CONFIGURATION ---
# The internal URL for Python to connect (Keep as settings.MINIO_ENDPOINT)
# The external URL for your browser to view images
# REPLACE THIS with your actual Server IP/Domain, e.g., "http://159.223.x.x:9000" or "https://files.resinen.com"
MINIO_PUBLIC_URL = os.getenv("MINIO_PUBLIC_URL", "http://72.61.105.138:9000") 

class StorageService:
    def __init__(self):
        # Connect to MinIO using the INTERNAL endpoint (Docker-to-Docker)
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            region_name="us-east-1"
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create the bucket if it doesn't exist."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except:
            # Bucket missing, let's create it
            try:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                
                # Make files publicly readable
                public_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {"AWS": ["*"]},
                            "Action": ["s3:GetObject"],
                            "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                        }
                    ]
                }
                self.s3_client.put_bucket_policy(
                    Bucket=self.bucket_name,
                    Policy=json.dumps(public_policy)
                )
                print(f"✅ [MinIO] Created Bucket: {self.bucket_name}")
            except Exception as e:
                print(f"⚠️ [MinIO] Could not create bucket: {e}")

    async def upload_file(self, file: UploadFile) -> str:
        """Uploads a file and returns the Public URL."""
        extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{extension}"
        
        try:
            # Upload using the internal client
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                unique_filename,
                ExtraArgs={"ContentType": file.content_type}
            )
        except NoCredentialsError:
            raise Exception("MinIO Credentials missing")
            
        # FIXED: Return the PUBLIC URL so the frontend can reach it
        return f"{MINIO_PUBLIC_URL}/{self.bucket_name}/{unique_filename}"

# Create a singleton instance
storage = StorageService()