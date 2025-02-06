
from sqlmodel import Field, SQLModel, Column, UniqueConstraint
from util.ulidtype import ULIDType
from ulid import ULID
from enum import Enum
from pydantic import BaseModel
from model.channels import Channel
from model.user import UserInfo

class OpenedChat(SQLModel, table=True):
    __tablename__ : str = "opened_chats"
    id: int | None = Field(default=None, primary_key=True)
    user_id: ULID = Field(..., default_factory=ULID, sa_column=Column(ULIDType))
    channel_id: ULID = Field(..., default_factory=ULID, sa_column=Column(ULIDType))

    __table_args__ = (UniqueConstraint("user_id", "channel_id", name="uix_user_id_target_id"),)

class OpenedChatResponse(BaseModel):
    channel: Channel
    users: list[UserInfo]