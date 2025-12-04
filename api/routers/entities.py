from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from kg_schemas.contextualisation import RDFStatement
from kg_schemas.errors import GenericErrorCodes

from api import logger
from api.functional.entities import (add_entity_f, get_entity_label,
                                     get_entity_properties)
from api.utils import session_wrapper

router = APIRouter(
    responses={d.value[0]: {"description": d.value[1]}
               for d in GenericErrorCodes}
)


@router.post("", response_model=str,summary="Add a new entity")
async def add_entity(
    statements: List[RDFStatement],
    entity_id: Optional[str] = None
    ):
    logger.info("Adding new entity")
    return session_wrapper(
        func=add_entity_f,
        entity_id=entity_id,
        statements=statements
    )


@router.get("", response_model=Dict[str,Any],summary="Get properties of an entity")
async def get_entity(
    entity_id: str
):
    logger.info("Retrieving properties of entity with id: %s", entity_id)
    return session_wrapper(
        func=get_entity_properties,
        entity_id=entity_id
    )

@router.get("/label", response_model=Dict[str,Any],summary="Get label of an entity")
async def get_entity(
    entity_id: str,
):
    logger.info("Retrieving label of entity with id: %s", entity_id)
    return session_wrapper(
        func=get_entity_label,
        entity_id=entity_id
    )