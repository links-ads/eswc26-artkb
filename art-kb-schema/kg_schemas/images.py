from typing import Optional
from kg_schemas import BaseModel

class ImagePayload(BaseModel):
    id: Optional[str] = None
    entity_id: str