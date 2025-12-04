import boto3
from qdrant_client import QdrantClient

from api.config import config


def get_qdrant_client():
    try:
        client = QdrantClient(url=config.qdrant_url, api_key=config.qdrant_api_key, timeout=20)
        yield client
    finally:
        pass

def get_minio_client():
    try:
        s3_client = boto3.client(
            "s3",
            endpoint_url=config.minio_url,
            aws_access_key_id=config.minio_root_user,
            aws_secret_access_key=config.minio_root_password,
        )
        yield s3_client
    finally:
        pass
    