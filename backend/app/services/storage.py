import boto3
from botocore.exceptions import NoCredentialsError
from fastapi import UploadFile
import uuid
import json

from app.core.config import settings

class StorageService:
    def __init__(self):
        # Connect to MinIO
        self.s3_client = boto3.client(
            's3',
            endpoint_url=settings.MINIO_ENDPOINT,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            region_name="us-east-1" # Required by library, ignored by MinIO
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
                
                # Make files publicly readable (so users can see images)
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
        # Generate unique filename to prevent overwrites
        # e.g. "avatar.jpg" -> "550e8400-e29b....jpg"
        extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{extension}"
        
        try:
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                unique_filename,
                ExtraArgs={"ContentType": file.content_type}
            )
        except NoCredentialsError:
            raise Exception("MinIO Credentials missing")
            
        # Return the URL
        return f"{settings.MINIO_ENDPOINT}/{self.bucket_name}/{unique_filename}"

# Create a singleton instance
storage = StorageService()