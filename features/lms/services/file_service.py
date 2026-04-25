"""MinIO Service"""

import os
import sys
from minio import Minio
from minio.error import S3Error
from fastapi import UploadFile, HTTPException, status
from core import settings
from core.log import logger


minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=False,
)
try:
    if not minio_client.bucket_exists(settings.MINIO_BUCKET_NAME):
        logger.info("Creating bucket : %s in minio...", settings.MINIO_BUCKET_NAME)
        minio_client.make_bucket(settings.MINIO_BUCKET_NAME)

        logger.info("Bucket %s created !", settings.MINIO_BUCKET_NAME)

except S3Error as error:
    logger.error("Minio error: %s", error)
    sys.exit()


async def save_in_minio(file: UploadFile):
    """Save uploaded file in minio"""

    try:
        minio_client.put_object(
            settings.MINIO_BUCKET_NAME,
            file.filename,
            file.file,
            file.size,
            content_type=file.content_type,
        )
        return f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{file.filename}"
    except S3Error as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error when uploading file: {e}",
        ) from e


async def save_certficate_in_minio(location: str):
    """Save generated file In MinIO or S3"""

    name = location.replace("tmp", "certificates")

    try:
        result = minio_client.fput_object(
            settings.MINIO_BUCKET_NAME,
            name,
            location,
        )

        # Remove the local file after uploading
        os.remove(location)

        object_name = result.object_name

        # Get the public URL
        file_url = f"http://{settings.MINIO_ENDPOINT}/{settings.MINIO_BUCKET_NAME}/{object_name}"

        logger.info("Saved in Minio !")

        return file_url

    except S3Error as exc:
        logger.error("Error when uploading file in minio: %s", str(exc))

    return None
