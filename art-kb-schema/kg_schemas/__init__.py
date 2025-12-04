from typing import Optional

from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        use_enum_values = True
    
class RDFDefinition(BaseModel):
    type:str
    value:str
    lang: Optional[str] = None
    datatype: Optional[str] = None