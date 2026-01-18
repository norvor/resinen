import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile
import uuid

from app.core.config import settings

class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            region_name="us-east-1" # MinIO ignores this, but boto3 requires it
        )
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """Create the bucket if it doesn't exist."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except:
            # If check fails, try creating it
            try:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
                # Make it public (Policy to allow reading files)
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
                import json
                self.s3_client.put_bucket_policy(
                    Bucket=self.bucket_name,
                    Policy=json.dumps(public_policy)
                )
                print(f"✅ Created Bucket: {self.bucket_name}")
            except Exception as e:
                print(f"⚠️ Could not create bucket: {e}")

    async def upload_file(self, file: UploadFile) -> str:
        """Uploads a file and returns the Public URL."""
        # 1. Generate unique filename (uuid + original extension)
        extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{extension}"
        
        # 2. Upload
        try:
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                unique_filename,
                ExtraArgs={"ContentType": file.content_type}
            )
        except NoCredentialsError:
            raise Exception("MinIO Credentials missing")
            
        # 3. Return URL
        # Format: http://localhost:9000/resinen-media/filename.jpg
        return f"{settings.MINIO_ENDPOINT}/{self.bucket_name}/{unique_filename}"

# Create a singleton instance to use elsewhere
storage = StorageService()