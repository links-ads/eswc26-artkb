
from fastapi import FastAPI, Security
from fastapi.logger import logger
from fastapi.middleware.cors import CORSMiddleware

from api import logger
from api.config import config
from api.routers import (cir, contextualisation, entities, files,
                         images, sparql)
from api.security import api_key_auth

app = FastAPI(root_path=config.api_url_prefix)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sparql.router, prefix="/sparql", dependencies=[Security(api_key_auth)], tags=["SPARQL"])
app.include_router(images.router, prefix="/images", dependencies=[Security(api_key_auth)], tags=["Images"])
app.include_router(entities.router, prefix="/entities", dependencies=[Security(api_key_auth)], tags=["Entities"])
app.include_router(contextualisation.router, prefix="/contextualisation", dependencies=[Security(api_key_auth)], tags=["Contextualisation"])
app.include_router(files.router, prefix="/files", dependencies=[Security(api_key_auth)], tags=["Files"])
app.include_router(cir.router, prefix="/cir", dependencies=[Security(api_key_auth)], tags=["Composed Image Retrieval"])


logger.info("Application startup completed")