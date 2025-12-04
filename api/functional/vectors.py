from qdrant_client import models


def add_vector(qdrant, vector, payload, collection_name=None):
    qdrant.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=payload['id'],
                payload=payload,
                vector=vector,
            )
        ]
    )

def vector_search(qdrant, vector, limit=10, collection_name=None):
    search_result = qdrant.search(
        collection_name=collection_name,
        query_vector=vector,
        limit=limit
    )
    return search_result