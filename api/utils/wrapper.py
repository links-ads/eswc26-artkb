from fastapi import HTTPException
from kg_schemas.errors import GenericErrorCodes
from pydantic.error_wrappers import ValidationError

from api import logger


def session_wrapper(
    minio=None,
    qdrant=None,
    func=None,
    **kwargs
):
    try:
        return func(minio=minio, qdrant=qdrant, **kwargs)
    except Exception as e:
        if isinstance(e, ValidationError):
            logger.error(str(e))
            raise HTTPException(*GenericErrorCodes.VALIDATION.value)
        elif isinstance(e, HTTPException):
            raise e
        else:
            logger.error(str(e))
            raise HTTPException(*GenericErrorCodes.INTERNAL_SERVER_ERROR.value)
