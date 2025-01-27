

from sqlmodel import Field, SQLModel, Column, Session, text
from util.ulidtype import ULIDType
from ulid import ULID
from enum import Enum
class Channel(SQLModel, table=True):
    __tablename__ : str = "channels"
    id: int | None = Field(default=None, primary_key=True)
    channel_id: ULID = Field(default_factory=ULID, sa_column=Column(ULIDType))
    channel_type: str

class ChannelType(str, Enum):
    user = "user"
    server = "server"

class ChannelUser(SQLModel, table=True):
    __tablename__ : str = "channel_users"
    id: int | None = Field(default=None, primary_key=True)
    channel_id: ULID = Field(default_factory=ULID, sa_column=Column(ULIDType))
    user_id: ULID = Field(default_factory=ULID, sa_column=Column(ULIDType))
    @staticmethod
    def find_user_channel(session: Session, user1: str, user2: str):
        query = text("""
            SELECT channel_users.channel_id
            FROM channel_users
            LEFT JOIN channels ON channels.channel_id = channel_users.channel_id
            WHERE user_id IN (:user1, :user2) AND channels.channel_type = 'user'
            GROUP BY channel_users.channel_id
            HAVING COUNT(DISTINCT user_id) = 2
        """).params(user1=str(user1), user2=str(user2))
        result = session.exec(query)
        return result.first()