import json
from typing import List

import requests
from kg_schemas.contextualisation import (EnablerResultSchema,
                                          MetadataInferRequestSchema,
                                          RDFDefinition, RDFStatement,
                                          SimilaritySearchResultSchema)
from pydantic import parse_obj_as

from api.config import config
from api.functional.entities import get_entity_properties
from api.functional.files import infer_content_type
from api.functional.vectors import vector_search
from api.utils.inference import triton_inference

SUGGESTED_PREDICATES = [
    "http://www.cidoc-crm.org/cidoc-crm/P45_consists_of",  # medium
    "http://w3id.org/cacao/CACAO_0000017",  # genre
    "http://w3id.org/cacao/CACAO_0000035",  # movement
    "http://www.cidoc-crm.org/cidoc-crm/P62_depicts",  # subject
]


def format_suggestions(suggestions) -> List[RDFStatement]:
    result = []
    for prop, values in suggestions.items():
        for obj in values:
            result.append(RDFStatement(
                property=RDFDefinition(type= "uri", value= prop),
                value=RDFDefinition(type= "uri", value= obj)
            ))
    return result


def transfer_metadata(
        scores_dict,
        metadata_dict,
        topk=5,
        predicates=[]    # attributes to be suggested
):
    """
    Suggest predicates' value for a query image, based on the top K most similar
    images in the database (given in the scores_dict) and their metadata (given
    in metadata_dict).
    The function ranks the values of each predicate based on the similarity
    scores of the top K images: the higher the similarity score, the more weight
    is given to the corresponding value of the predicate.
    The function returns a dictionary containing the suggested value for each
    requested predicate, in descending order of computed score.
    Args:
    - scores_dict: dictionary containing as keys the most similar images to the query and as values the corresponding similarity scores
    - metadata_dict: dictionary containing predicates and their values for each of the most similar images in scores_dict
    - topk: number of most similar images to consider (int)
    - predicates: list of predicates to suggest metadata for

    Returns:
    - metadata_suggestions: dictionary containing suggested value for each requested predicate
    """

    metadata_suggestions = {}

    # Get the top K artifacts
    topk_artifacts = sorted(scores_dict.items(),
                            key=lambda x: x[1], reverse=True)[:topk]

    # Iterate over each predicate
    for predicate in predicates:
        ranking = {}    # this ranking ranks the values of the predicate

        # Iterate over each top K artifact
        for artifact, sim in topk_artifacts:

            # Look for current predicate in metadata_dict and get the corresponding value(s)
            artifact_meta = metadata_dict[artifact]  # list of predicates
            values = [p['value']['value']
                      for p in artifact_meta if p['property']['value'] == predicate]

            # Iterate over each predicate value
            for v in values:
                # Add value to the ranking
                ranking[v] = ranking.get(v, 0) + sim**2

        # Sort the ranking dictionary by value in descending order
        ranking = dict(
            sorted(ranking.items(), key=lambda x: x[1], reverse=True))

        # Add the predicate's ranking of values to the metadata_suggestions dictionary
        metadata_suggestions[predicate] = ranking

    return metadata_suggestions


def metadata_suggestion_f(image_bytes: bytes, limit: int, qdrant, ** kwargs) -> List[RDFStatement]:
    anchors = similarity_search_f(
        image_bytes=image_bytes,
        limit=limit,
        qdrant=qdrant)
    entities = [MetadataInferRequestSchema(
        entity_id=anchor.entity_id,
        score=anchor.score
    ) for anchor in anchors]
    return metadata_infer_f(
        entities=entities
    )
        

def similarity_search_f(image_bytes: bytes, limit: int, qdrant, **kwargs) -> List[SimilaritySearchResultSchema]:
    image_vector = triton_inference(
        service_cfg=config.triton_config.universal_embedder,
        img_bytes=image_bytes,
        triton_ssl=config.triton_ssl,
        max_retries=config.triton_max_retries
    ).tolist()
    search_result = vector_search(qdrant, vector=image_vector, limit=limit,collection_name=config.qdrant_collection_name)
    return [SimilaritySearchResultSchema(image_id= result.id, entity_id= result.payload['entity_id'], score= result.score) for result in search_result]

def metadata_infer_f(entities: List[MetadataInferRequestSchema], **kwargs) -> List[RDFStatement]:
    """
    Infer metadata from a list of entities.
    """
    anchors_metadata = {
        (entity_id := entity.entity_id): get_entity_properties(entity_id)['results']['bindings']
        for entity in entities
    }
    anchors_scores = {
        entity.entity_id: entity.score
        for entity in entities
    }
    return format_suggestions(transfer_metadata(
        scores_dict=anchors_scores,
        metadata_dict=anchors_metadata,
        topk=len(entities),
        predicates=SUGGESTED_PREDICATES
    ))
