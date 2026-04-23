from pydantic_core.core_schema import AfterValidatorFunctionSchema

from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _, __) -> AfterValidatorFunctionSchema:
        from pydantic_core import core_schema

        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.any_schema()
        )
    
    @classmethod
    def validate(cls, v) -> str | None:
        if v is None:
            return None
        
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str):
            return v
        raise ValueError("Invalid ObjectId")