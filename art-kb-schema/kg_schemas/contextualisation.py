from kg_schemas import BaseModel, RDFDefinition


class RDFStatement(BaseModel):
    property: RDFDefinition
    value: RDFDefinition

class SimilaritySearchResultSchema(BaseModel):
    image_id: str
    entity_id: str
    score: float

class MetadataInferRequestSchema(BaseModel):
    entity_id: str
    score: float

class EnablerResultSchema(BaseModel):
    property: RDFDefinition
    value: RDFDefinition
    source: str