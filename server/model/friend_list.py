from sqlmodel import Field, SQLModel


class FriendListEntry(SQLModel, table=True):
    __tablename__ : str = "friend_list"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    friend_id: int = Field(foreign_key="user.id")
    pending: bool = True
    date_added: int | None
