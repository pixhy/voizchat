
from sqlalchemy.types import TypeDecorator, CHAR
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from ulid import ULID

class ULIDType(TypeDecorator):
    impl = CHAR
    cache_ok = True

    def __init__(self):
        super().__init__(length=26, )

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, ULID):
            return str(value)
        if isinstance(value, str):
            return value
        raise ValueError(f"Expected ULID, got {type(value)}")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return ULID.from_str(value)

    def process_literal_param(self, value, dialect):
        return str(value) if value is not None else None

    def copy(self, **kwargs):
        return ULIDType()

    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: type, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        return core_schema.str_schema()

    @staticmethod
    def validate(value: str) -> ULID:
        return ULID.from_str(value)

