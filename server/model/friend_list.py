from sqlmodel import Field, SQLModel
from pydantic import BaseModel
from model.user import UserInfo


class FriendListEntry(SQLModel, table=True):
    __tablename__ : str = "friend_list"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    friend_id: int = Field(foreign_key="user.id")
    pending: bool = True
    date_added: int | None


class FriendStateUpdate(BaseModel):
    other_user: UserInfo
    new_state: str # accept-outgoing, accept-incoming, request-incoming, request-outgoing, remove-friend, remove-incoming, remove-outgoing
