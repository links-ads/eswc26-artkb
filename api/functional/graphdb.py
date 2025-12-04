from typing import Dict

import requests
from fastapi import HTTPException
from kg_schemas.errors import error_codes

from api.config import config


def run_sparql_query(query: str, update:bool=False, **kwargs) -> Dict:
    url = f"{config.graphdb_url}/repositories/{config.graphdb_repo_name}"
    if update:
        url += "/statements"

    headers = {
        'Content-Type': 'application/sparql-update' if update else 'application/sparql-query',
        'Accept': 'application/json',
    }

    response = requests.request(
        "POST", url, headers=headers, data=query, auth=config.graphdb_auth)
    ref_code = 204 if update else 200
    if response.status_code != ref_code:
        raise HTTPException(*error_codes[response.status_code])
    return (response.json()) if not update else {}
