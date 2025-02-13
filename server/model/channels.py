

from sqlmodel import Field, SQLModel, Column, Session, text, select
from util.ulidtype import ULIDType
from ulid import ULID
from enum import Enum
from model.user import User
from model.message import Message
class Channel(SQLModel, table=True):
    __tablename__ : str = "channels"
    id: int | None = Field(default=None, primary_key=True)
    channel_id: ULID = Field(default_factory=ULID, sa_column=Column(ULIDType))
    channel_type: str
    last_update: int
    def get_users(self, session: Session, skip_user: User = None) -> list[User]:
        return [
            user
            for user in session.exec(
                select(User)
                .join(ChannelUser, ChannelUser.user_id == User.userid)
                .where(ChannelUser.channel_id == self.channel_id)
            )
            if not skip_user or skip_user.id != user.id
        ]

class ChannelType(str, Enum):
    user = "user"
    server = "server"


class ChannelUser(SQLModel, table=True):
    __tablename__ : str = "channel_users"
    id: int | None = Field(default=None, primary_key=True)
    channel_id: ULID = Field(default_factory=ULID, sa_column=Column(ULIDType))
    user_id: ULID = Field(default_factory=ULID, sa_column=Column(ULIDType))
    last_read_message_id: int | None = Field(foreign_key="messages.id")
    @staticmethod
    def find_user_channel(session: Session, user1: str, user2: str) -> Channel | None:
        query = text("""
            SELECT channels.id
            FROM channel_users
            LEFT JOIN channels ON channels.channel_id = channel_users.channel_id
            WHERE user_id IN (:user1, :user2) AND channels.channel_type = 'user'
            GROUP BY channel_users.channel_id
            HAVING COUNT(DISTINCT user_id) = 2
        """).params(user1=str(user1), user2=str(user2))
        result = session.exec(query).first()
        if result:
            return session.get(Channel, result[0])
        return None
    @staticmethod
    def update_last_read_message_id(session: Session, user: str, message: Message) -> None:
        query = text("""
            UPDATE channel_users 
            SET last_read_message_id = :message_id 
            WHERE channel_id = :channel_id 
            AND user_id = :user_id
            AND (last_read_message_id IS NULL OR last_read_message_id < :message_id)
        """).params(
            user_id = user,
            message_id = message.id,
            channel_id = str(message.channel_id)
        )
        session.exec(query)
        session.commit()