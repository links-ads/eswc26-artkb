from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile
from kg_schemas.errors import GenericErrorCodes

from api import logger
from api.clients import get_minio_client, get_qdrant_client
from api.config import config
from api.functional.files import get_file_by_id
from api.functional.images import upload_image
from api.utils import session_wrapper

router = APIRouter(
    responses={d.value[0]: {"description": d.value[1]}
               for d in GenericErrorCodes}
)


@router.get("/{image_id}", summary="Get Image by ID")
async def get_image(
    image_id: str,
    minio=Depends(get_minio_client)
):
    logger.info("Retrieving image with id: %s", image_id)
    img_bytes, content_type = session_wrapper(
        minio=minio,
        func=get_file_by_id,
        file_id=image_id,
        bucket_name=config.minio_image_bucket_name
    )
    return Response(content=img_bytes.getvalue(), media_type=content_type)


@router.post("", response_model=str, summary="Upload an image to all collections")
async def add_image(
    file: Annotated[UploadFile, File()],
    payload: Annotated[str, Form()],
    minio=Depends(get_minio_client),
    qdrant=Depends(get_qdrant_client)
):
    image_bytes = await file.read()
    filename = file.filename
    logger.info("Uploading new image with filename: %s", filename)
    return session_wrapper(
        minio=minio,
        qdrant=qdrant,
        func=upload_image,
        image_bytes=image_bytes,
        payload=payload
    )

