from sqlmodel import Field, SQLModel


class BlockListEntry(SQLModel, table=True):
    __tablename__ : str = "block_list"
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    blocked_id: int = Field(foreign_key="user.id")
    date_blocked: int