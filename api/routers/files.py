from typing import Annotated
from api import logger
from api.config import config
from fastapi import APIRouter, Depends, Response, UploadFile, File
from api.utils import session_wrapper
from api.functional.files import upload_file_content, get_file_by_id
from api.clients import get_minio_client
from kg_schemas.errors import GenericErrorCodes


router = APIRouter(
    responses={d.value[0]: {"description": d.value[1]}
               for d in GenericErrorCodes}
)


@router.get("/{file_id}", summary="Get File by ID")
async def get_file(
    file_id: str,
    minio=Depends(get_minio_client)
):
    logger.info("Retrieving file with id: %s", file_id)
    img_bytes, content_type = session_wrapper(
        minio=minio,
        func=get_file_by_id,
        file_id=file_id,
        bucket_name=config.minio_file_bucket_name
    )
    return Response(content=img_bytes.getvalue(), media_type=content_type)


@router.post("", response_model=str, summary="Upload a file")
async def add_file(
    file: Annotated[UploadFile, File()],
    minio=Depends(get_minio_client),
):
    file_bytes = await file.read()
    filename = file.filename
    logger.info("Uploading new file : %s", filename)
    return session_wrapper(
        minio=minio,
        func=upload_file_content,
        file_bytes=file_bytes,
        file_id=None,
        bucket_name=config.minio_file_bucket_name,
    )
