from pydantic import BaseModel
from pydantic.alias_generators import to_camel

class CamelCaseModel(BaseModel):
    class Config:
        # This tells Pydantic to generate camelCase aliases for all fields
        alias_generator = to_camel
        # This allows the model to be populated by either the original snake_case name or the camelCase alias
        populate_by_name = True