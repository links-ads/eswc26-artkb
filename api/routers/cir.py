from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from api.clients import get_qdrant_client
from api.functional.cir import cir_f
from api.utils import session_wrapper

router = APIRouter()


@router.post("/retrieve/", summary="Composed image retrieval", description="Retrieve an image based on a composed query image.")
async def composed_image_retrieval(
    file: Annotated[UploadFile, File()],
    query: str,
    limit: int = 5,
    qdrant=Depends(get_qdrant_client)
):
    image_bytes = await file.read()
    
    return session_wrapper(
        func=cir_f,
        image_bytes=image_bytes,
        query=query,
        limit=limit,
        qdrant=qdrant
    )