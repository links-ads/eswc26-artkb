import json
import uuid

from kg_schemas.images import ImagePayload

from api.config import config
from api.functional.files import upload_file_content
from api.functional.vectors import add_vector
from api.utils.inference import triton_inference

def upload_image(minio, image_bytes: bytes, qdrant, payload: str, ** kwargs) -> str:
    payload = ImagePayload(**json.loads(payload))
    if not payload.id:
        payload.id = str(uuid.uuid4())
    # Add image to MinIO collection
    upload_file_content(
        minio=minio,
        file_bytes=image_bytes,
        file_id=payload.id,
        bucket_name=config.minio_image_bucket_name
    )
    # Add image vector to Qdrant collection
    image_vector = triton_inference(
        service_cfg=config.triton_config.universal_embedder,
        img_bytes=image_bytes,
        triton_ssl=config.triton_ssl,
        max_retries=config.triton_max_retries
    ).tolist()
    add_vector(qdrant, image_vector, payload.dict(),config.qdrant_collection_name)
    return payload.id