from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

from api.config import config


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


async def api_key_auth(api_key: str = Security(api_key_header)):
    if api_key != config.api_secret:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")