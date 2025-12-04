from typing import Any, Dict, List
from uuid import uuid4

from kg_schemas.contextualisation import RDFStatement
from rdflib import Graph, Literal, URIRef

from api.functional.graphdb import run_sparql_query

BASE_PART_URI = "http://w3id.org/cacao/vocab/part/"


def get_entity_properties(entity_id:str, **kwargs) -> Dict[str,Any]:
    query = f"""
    SELECT ?property ?value
    WHERE {{
        <{entity_id}> ?property ?value
    }}
    """
    return run_sparql_query(query, **kwargs)

def get_entity_label(entity_id:str, **kwargs) -> Dict[str,Any]:
    query = f"""
    SELECT ?label
    WHERE {{
        <{entity_id}> rdfs:label ?label .
    }}
    """
    return run_sparql_query(query, **kwargs)

def add_entity_f(entity_id:str,statements:List[RDFStatement], **kwargs) -> Dict[str,Any]:
    g = Graph()
    if entity_id:
        entity_uri = URIRef(entity_id)
    else:
        entity_uri = URIRef(BASE_PART_URI + str(uuid4()))

    # Aggiungi le altre proprietà
    for st in statements:
        p = URIRef(st.property.value)
        v = st.value
        if v.type == "uri":
            o = URIRef(v.value)
        elif v.type == "literal":
            o = Literal(v.value, lang=v.lang) if v.lang else Literal(v.value)
        else:
            continue
        g.add((entity_uri, p, o))

    # Serializza e invia a GraphDB
    insert_query = f"INSERT DATA {{ {g.serialize(format='nt')} }}"
    run_sparql_query(insert_query, content_type='application/sparql-update', update=True, **kwargs)
    return str(entity_uri)