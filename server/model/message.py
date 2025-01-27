from typing import Annotated
from sqlmodel import Field, SQLModel, Column
from util.ulidtype import ULIDType
from pydantic import BaseModel, StringConstraints
from ulid import ULID


class Message(SQLModel, table=True):
    __tablename__ : str = "messages"
    id: int | None = Field(default=None, primary_key=True)
    channel_id: ULID = Field(default_factory=ULID, sa_column=Column(ULIDType))
    sender_id: ULID = Field(default_factory=ULID, sa_column=Column(ULIDType))
    message: str
    created_at: int

class NewMessage(BaseModel):
    message: Annotated[str, StringConstraints(max_length=512)]