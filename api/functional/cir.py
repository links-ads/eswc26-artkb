from kg_schemas.contextualisation import SimilaritySearchResultSchema

from api.config import config
from api.functional.vectors import vector_search
from api.utils.inference import triton_inference

def cir_f(
        image_bytes: bytes,
        query: str,
        qdrant,
        limit: int = 5,
        **kwargs
):
    image_vector = triton_inference(
        service_cfg=config.triton_config.universal_embedder,
        img_bytes=image_bytes,
        text=query,
        triton_ssl=config.triton_ssl,
        max_retries=config.triton_max_retries
    ).tolist()
    search_result = vector_search(qdrant, vector=image_vector, limit=limit,collection_name=config.qdrant_collection_name)
    return [SimilaritySearchResultSchema(image_id= result.id, entity_id= result.payload['entity_id'], score= result.score) for result in search_result]