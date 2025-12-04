from typing import Any, Dict

from fastapi import APIRouter, Body
from kg_schemas.errors import GenericErrorCodes

from api import logger
from api.functional.graphdb import run_sparql_query
from api.utils import session_wrapper

router = APIRouter(
    responses={d.value[0]: {"description": d.value[1]}
               for d in GenericErrorCodes}
)


@router.post("", response_model=Dict[str, Any], summary="Run SPARQL query")
async def run_sparql_post(
    query: str = Body(media_type="application/sparql-query"),
    update: bool = False
):
    logger.info("Received SPARQL query: %s", query)
    return session_wrapper(
        func=run_sparql_query,
        query=query,
        update=update
    )
