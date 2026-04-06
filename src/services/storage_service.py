import os
import uuid
import logging
from pathlib import Path
from typing import Optional

from src.core.config import settings

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path(getattr(settings, "UPLOAD_DIR", "uploads"))

class StorageService:
    """Local-disk storage with optional S3 fallback."""

    def __init__(self) -> None:
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    def _local_path(self, filename: str) -> Path:
        return UPLOAD_DIR / filename

    async def upload_file(self, filename: str, content_type: str, data: bytes, user_id: int) -> str:
        """Save file to disk and return its accessible URL."""
        ext = Path(filename).suffix
        unique_name = f"{user_id}_{uuid.uuid4().hex}{ext}"
        dest = self._local_path(unique_name)
        dest.write_bytes(data)
        logger.info("Stored file %s (%d bytes) for user %d", unique_name, len(data), user_id)
        if getattr(settings, "USE_S3", False):
            return await self._upload_to_s3(unique_name, content_type, data)
        return f"/static/uploads/{unique_name}"

    async def _upload_to_s3(self, key: str, content_type: str, data: bytes) -> str:
        import boto3
        from botocore.exceptions import BotoCoreError
        s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )
        s3.put_object(Bucket=settings.S3_BUCKET, Key=key, Body=data, ContentType=content_type)
        return f"https://{settings.S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{key}"

    async def delete_file(self, filename: str) -> bool:
        """Remove a file from local disk."""
        path = self._local_path(filename)
        if path.exists():
            path.unlink()
            logger.info("Deleted file %s", filename)
            return True
        return False

    def get_url(self, filename: str) -> str:
        """Return the public URL for a stored file."""
        return f"/static/uploads/{filename}"