from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile
from kg_schemas.contextualisation import (MetadataInferRequestSchema,
                                          RDFStatement,
                                          SimilaritySearchResultSchema)
from kg_schemas.errors import GenericErrorCodes

from api import logger
from api.clients import get_qdrant_client
from api.functional.contextualisation import (metadata_infer_f,
                                              metadata_suggestion_f,
                                              similarity_search_f)
from api.utils import session_wrapper

router = APIRouter(
    responses={d.value[0]: {"description": d.value[1]}
               for d in GenericErrorCodes}
)


@router.post("/", summary="Suggest metadata for an image", response_model=List[RDFStatement])
async def suggest_metadata(
    file: Annotated[UploadFile, File()],
    limit: Optional[int] = Form(5),
    qdrant=Depends(get_qdrant_client)
):
    image_bytes = await file.read()
    filename = file.filename
    logger.info("Suggesting metadata for image with filename: %s", filename)
    
    return session_wrapper(
        qdrant=qdrant,
        func=metadata_suggestion_f,
        image_bytes=image_bytes,
        limit=limit
    )

@router.post("/search", summary="Search similar images",response_model=List[SimilaritySearchResultSchema])
async def similarity_search(
    file: Annotated[UploadFile, File()],
    limit: Optional[int] = Form(5),
    qdrant=Depends(get_qdrant_client)
):
    image_bytes = await file.read()
    filename = file.filename
    logger.info("Searching similar images for image with filename: %s", filename)
    
    return session_wrapper(
        qdrant=qdrant,
        func=similarity_search_f,
        image_bytes=image_bytes,
        limit=limit
    )

@router.post("/infer", summary="Infer metadata from a list of entities",response_model=List[RDFStatement])
async def infer_metadata(
    entities: List[MetadataInferRequestSchema]
):
    
    logger.info("Infering metadata from a list of entities",)
    
    return session_wrapper(
        func=metadata_infer_f,
        entities=entities
    )