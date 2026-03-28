"""
File storage service for MinIO/S3 object storage.
Handles profile pictures, service documents, and media files.
"""

from typing import Optional
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings


def get_s3_client():
    """Get boto3 S3 client for MinIO."""
    try:
        return boto3.client(
            "s3",
            endpoint_url=settings.MINIO_URL,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            region_name="us-east-1",
        )
    except Exception as e:
        print(f"[ERROR] Failed to create S3 client: {str(e)}")
        return None


def ensure_bucket_exists(bucket_name: str = None) -> bool:
    """Create bucket if it doesn't exist."""
    if bucket_name is None:
        bucket_name = settings.MINIO_BUCKET

    client = get_s3_client()
    if not client:
        return False

    try:
        client.head_bucket(Bucket=bucket_name)
        print(f"[OK] Bucket '{bucket_name}' exists")
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            try:
                client.create_bucket(Bucket=bucket_name)
                print(f"[OK] Created bucket '{bucket_name}'")
                return True
            except Exception as e:
                print(f"[ERROR] Failed to create bucket: {str(e)}")
                return False


async def upload_file(
    file_content: bytes,
    file_key: str,
    bucket_name: str = None,
    content_type: str = "application/octet-stream",
) -> Optional[str]:
    """
    Upload file to MinIO.

    Args:
        file_content: File content bytes
        file_key: S3 object key (path)
        bucket_name: S3 bucket name
        content_type: MIME type

    Returns:
        File URL if successful, None otherwise
    """
    if bucket_name is None:
        bucket_name = settings.MINIO_BUCKET

    client = get_s3_client()
    if not client:
        return None

    try:
        # Ensure bucket exists
        ensure_bucket_exists(bucket_name)

        # Upload file
        client.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=file_content,
            ContentType=content_type,
        )

        file_url = f"{settings.MINIO_URL}/{bucket_name}/{file_key}"
        print(f"[OK] File uploaded: {file_url}")
        return file_url

    except Exception as e:
        print(f"[ERROR] Failed to upload file {file_key}: {str(e)}")
        return None


async def download_file(
    file_key: str, bucket_name: str = None
) -> Optional[bytes]:
    """
    Download file from MinIO.

    Args:
        file_key: S3 object key
        bucket_name: S3 bucket name

    Returns:
        File content bytes if successful, None otherwise
    """
    if bucket_name is None:
        bucket_name = settings.MINIO_BUCKET

    client = get_s3_client()
    if not client:
        return None

    try:
        response = client.get_object(Bucket=bucket_name, Key=file_key)
        content = response["Body"].read()
        return content
    except Exception as e:
        print(f"[ERROR] Failed to download file {file_key}: {str(e)}")
        return None


async def delete_file(file_key: str, bucket_name: str = None) -> bool:
    """
    Delete file from MinIO.

    Args:
        file_key: S3 object key
        bucket_name: S3 bucket name

    Returns:
        True if successful, False otherwise
    """
    if bucket_name is None:
        bucket_name = settings.MINIO_BUCKET

    client = get_s3_client()
    if not client:
        return False

    try:
        client.delete_object(Bucket=bucket_name, Key=file_key)
        print(f"[OK] File deleted: {file_key}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to delete file {file_key}: {str(e)}")
        return False


async def upload_profile_picture(
    user_id: int, file_content: bytes
) -> Optional[str]:
    """Upload user profile picture."""
    file_key = f"profiles/{user_id}/avatar.jpg"
    return await upload_file(file_content, file_key, content_type="image/jpeg")


async def upload_service_document(
    service_id: int, filename: str, file_content: bytes
) -> Optional[str]:
    """Upload service-related document."""
    file_key = f"services/{service_id}/{filename}"
    return await upload_file(file_content, file_key, content_type="application/pdf")


async def upload_technician_certificate(
    technician_id: int, certificate_type: str, file_content: bytes
) -> Optional[str]:
    """Upload technician certificate/qualification."""
    file_key = f"technicians/{technician_id}/certificates/{certificate_type}.pdf"
    return await upload_file(file_content, file_key, content_type="application/pdf")


async def list_files(prefix: str = "", bucket_name: str = None) -> Optional[list]:
    """
    List files with given prefix.

    Args:
        prefix: S3 key prefix
        bucket_name: S3 bucket name

    Returns:
        List of file keys if successful, None otherwise
    """
    if bucket_name is None:
        bucket_name = settings.MINIO_BUCKET

    client = get_s3_client()
    if not client:
        return None

    try:
        response = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        files = [obj["Key"] for obj in response.get("Contents", [])]
        return files
    except Exception as e:
        print(f"[ERROR] Failed to list files: {str(e)}")
        return None
