import boto3
from src.settings import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.S3_ACCESS_KEY_ID,
    aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
    # region_name=settings.aws_region,
    endpoint_url=settings.S3_BUCKET_URL
)