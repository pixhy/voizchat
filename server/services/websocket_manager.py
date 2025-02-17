from fastapi import WebSocket
from fastapi.websockets import WebSocketState
from pydantic import BaseModel

from sqlmodel import select, Session

from model.channels import Channel, ChannelUser
from model.user import User

class Message(BaseModel):
    cmd: str
    data: BaseModel
    def model_dump(self, **kwargs):
        base_dict = super().model_dump(**kwargs)
        print(self.data)
        if isinstance(self.data, BaseModel):
            base_dict['data'] = self.data.model_dump(**kwargs)
        print(base_dict)
        return base_dict
    def model_dump_json(self, **kwargs):
        return super().model_dump_json(**kwargs).replace('"data":{}', '"data":' + self.data.model_dump_json(**kwargs))

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = dict()

    async def connect(self, websocket: WebSocket, user: User):

        self.active_connections.setdefault(user.userid, []).append(websocket)

    def disconnect(self, websocket: WebSocket):
        for user_list in self.active_connections.values():
            user_list.remove(websocket)

    async def broadcast_to_user(self, user_id: str, command: str, obj: BaseModel):
        print("broadcast to user", user_id, command)
        websockets = self.active_connections.get(user_id)
        json_str = Message(cmd=command, data=obj).model_dump_json()
        if websockets:
            for websocket in websockets:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_text(json_str)
        else:
            print("no websockets for user", user_id)

    async def broadcast_to_channel(self, session: Session, channel: Channel, command: str, obj: BaseModel, skip_user: User = None):
        users = session.exec(select(ChannelUser.user_id).where(ChannelUser.channel_id == channel.channel_id)).all()
        for user_id in users:
            if not skip_user or skip_user.userid != user_id:
                await self.broadcast_to_user(user_id, command, obj)


