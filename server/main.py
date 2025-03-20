import hashlib
import os
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, Response,  WebSocket, WebSocketDisconnect, status, WebSocketException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, SQLModel, create_engine, select, text
from base64 import b64encode, b64decode
import jwt
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import time
from enum import Enum

from email_service import send_verification_email
from model.opened_chat import OpenedChat, OpenedChatResponse
from services.websocket_manager import ConnectionManager
from model.user import User, CreateUserRequest, PrivateUserInfo, LoginRequest, UserInfo
from model.friend_list import FriendListEntry, FriendStateUpdate
from model.message import Message, NewMessage
from model.channels import Channel, ChannelUser, ChannelType
from model.whiteboard import WhiteboardDrawData
from dotenv import load_dotenv

import logging
#logging.basicConfig()
#sqlalchemy_logging = logging.getLogger('sqlalchemy.engine')
#sqlalchemy_logging.setLevel(logging.DEBUG)
load_dotenv()

sqlite_url = os.getenv("DATABASE_URL") or "sqlite:///data/voizchat.db"
print(f"Using database: {sqlite_url}")
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def hash_password(password: str):
    salt = os.urandom(32)
    passwordhash = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1)
    return f"1${b64encode(salt).decode('utf-8')}${b64encode(passwordhash).decode('utf-8')}"

def verify_password_hash(password_hash, password):
    version, salt, expected_hash = password_hash.split('$')
    if version != "1": return False
    salt = b64decode(salt)
    expected_hash = b64decode(expected_hash)
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1) == expected_hash


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    

def initialize_users(session: Session):
    if not session.exec(select(User)).all():
        test_users = [
            User(email="test1@example.com", username="test1", passwordhash=hash_password("asdf"), is_verified=True),
            User(email="test2@example.com", username="test2", passwordhash=hash_password("asdf"), is_verified=True),
            User(email="test3@example.com", username="test3", passwordhash=hash_password("asdf"), is_verified=True),
            User(email="test4@example.com", username="test4", passwordhash=hash_password("asdf"), is_verified=True),
            User(email="test5@example.com", username="test5", passwordhash=hash_password("asdf"), is_verified=True),
            User(email="test6@example.com", username="test6", passwordhash=hash_password("asdf"), is_verified=True),
            User(email="test7@example.com", username="test7", passwordhash=hash_password("asdf"), is_verified=True),
            User(email="test8@example.com", username="test8", passwordhash=hash_password("asdf"), is_verified=True),
            User(email="test9@example.com", username="test9", passwordhash=hash_password("asdf"), is_verified=True),
        ]
        session.add_all(test_users)
        session.add_all([
            FriendListEntry(user_id=1, friend_id=4, pending=False),
            FriendListEntry(user_id=1, friend_id=5, pending=True),
            FriendListEntry(user_id=1, friend_id=7, pending=True),
            FriendListEntry(user_id=1, friend_id=9, pending=False),
            FriendListEntry(user_id=2, friend_id=1, pending=False),
            FriendListEntry(user_id=2, friend_id=9, pending=False),
            FriendListEntry(user_id=3, friend_id=7, pending=False),
            FriendListEntry(user_id=4, friend_id=5, pending=False),
            FriendListEntry(user_id=6, friend_id=1, pending=True),
            FriendListEntry(user_id=6, friend_id=7, pending=False),
            FriendListEntry(user_id=7, friend_id=2, pending=False),
            FriendListEntry(user_id=7, friend_id=5, pending=False),
            FriendListEntry(user_id=8, friend_id=3, pending=False),
            FriendListEntry(user_id=8, friend_id=1, pending=True),
        ])
        session.commit()
    


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    hash(_app)
    create_db_and_tables()
    with Session(engine) as session:
        initialize_users(session)
    yield
    # Cleanup
    pass

app = FastAPI(lifespan=lifespan)


origins = [
    "http://localhost:5173",  # Vite's default dev server
    "http://127.0.0.1:5173"  # Alternative localhost
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



jwt_public_key = os.getenv("AUTH_JWT_PUBKEY")
if jwt_public_key:
    jwt_public_key = f'-----BEGIN PUBLIC KEY-----\n{jwt_public_key}\n-----END PUBLIC KEY-----'
else:
    with open("public_key.pem", "r") as public_file:
        jwt_public_key = public_file.read()

jwt_private_key = os.getenv("AUTH_JWT_PRIVKEY")
if jwt_private_key:
    jwt_private_key = f'-----BEGIN PRIVATE KEY-----\n{jwt_private_key}\n-----END PRIVATE KEY-----'
else:
    with open("private_key.pem", "r") as private_file:
        jwt_private_key = private_file.read()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")
credentials_exception = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
    try:
        payload = jwt.decode(token, jwt_public_key, algorithms=["EdDSA"])
        user_id: int = payload.get("uid")
        if user_id is None:
            print("token has no uid")
            raise credentials_exception
    except jwt.InvalidTokenError as e:
        print(e)
        raise credentials_exception
    user = session.get(User, user_id)
    if user is None:
        print("user not found")
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_verified:
        raise HTTPException(status_code=400, detail="Unverified user")
    return current_user

UserDep = Annotated[User, Depends(get_current_active_user)]

async def get_active_user_by_token(token: str, session: Session):
    try:
        payload = jwt.decode(token, jwt_public_key, algorithms=["EdDSA"])
        user_id: int = payload.get("uid")
        if user_id is None:
            return None
    except jwt.InvalidTokenError as e:
        return None
    user = session.get(User, user_id)
    if user is None or not user.is_verified:
        return None
    return user


manager = ConnectionManager()

async def receive_websocket_cmd(ws: WebSocket):
    data = await ws.receive_json()
    try:
        return data["cmd"], data["data"]
    except Exception as e:
        print(e)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket, session: SessionDep):
    await websocket.accept()

    data = await websocket.receive_json()
    try:
        if data["cmd"] == "login":
            token = data["data"]["token"]
            current_user = await get_active_user_by_token(token, session)
            if not current_user:
                raise ValueError("cannot authenticate user")
        else:
            raise ValueError("command is not login")
    except Exception as e:
        print(e)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    await manager.connect(websocket, current_user)
    try:
        while True:
            (cmd, data) = await receive_websocket_cmd(websocket)
            if cmd == "read_message":
                message_id = data.get("message_id")
                message = session.get(Message, message_id)
                ChannelUser.update_last_read_message_id(session, str(current_user.userid), message)
            elif cmd == "whiteboard":
                channel_id = data.get("channel_id")
                channel = session.exec(select(Channel).where(Channel.channel_id == channel_id)).first()
                if channel:
                    await manager.broadcast_to_channel(
                        session,
                        channel,
                        "whiteboard",
                        WhiteboardDrawData(**data),
                        current_user
                    )
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/api/users/register", response_model=dict)
def create_user(user_request: CreateUserRequest, session: SessionDep):
    user = User(email=user_request.email, username=user_request.username)
    user.passwordhash = hash_password(user_request.password)
    session.add(user)
    session.commit()
    session.refresh(user)

    user.verification_code = os.urandom(20).hex()
    user.verification_code_expiration = int(time.time()) + 60 * 60 * 24  # one day
    send_verification_email(user_request.email, user.verification_code)

    session.commit()

    one_week_in_seconds = 60 * 60 * 24 * 7
    expiration = int(time.time()) + one_week_in_seconds
    payload = {"uid": user.id, "exp": expiration}
    token = jwt.encode(payload, jwt_private_key, algorithm="EdDSA")

    response = {
        "token": token,
        "user": UserInfo(userid=str(user.userid), username=user.username)
    }

    return response

@app.get("/api/users/verify/{verification_code}")
def verify_user(verification_code: str, session: SessionDep):
    user = session.exec(select(User).where(User.verification_code == verification_code)).first()
    if user:
        user.is_verified = True
        user.verification_code = None
        user.verification_code_expiration = None
        session.commit()
        session.refresh(user)
        return Response(status_code=204)
    
    raise HTTPException(status_code=404, detail="Verification code not found")


@app.post("/api/users/login", response_model=dict)
def login_user(user_request: LoginRequest, session: SessionDep):
    user = session.exec(select(User).where(User.email == user_request.email)).first()

    if not user or not verify_password_hash(user.passwordhash, user_request.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    one_week_in_seconds = 60 * 60 * 24 * 7
    expiration = int(time.time()) + one_week_in_seconds
    payload = {"uid": user.id, "exp": expiration}
    token = jwt.encode(payload, jwt_private_key, algorithm="EdDSA")

    return {
        "token": token,
        "user": UserInfo(userid=str(user.userid), username=user.username)
    }

@app.post("/api/users/token")
def login_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep) -> dict[str, str]:
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password_hash(user.passwordhash, form_data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    one_week_in_seconds = 60*60*24*7
    expiration = int(time.time()) + one_week_in_seconds
    payload = {"uid": user.id, "exp": expiration}
    token = jwt.encode(payload, jwt_private_key, algorithm="EdDSA")
    return jsonable_encoder({"access_token": token, "token_type": "bearer"})

@app.get("/api/users/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[UserInfo]:
    return [
        UserInfo.from_user(user)
             for user in session.exec(select(User).offset(offset).limit(limit)).all()
    ]

@app.get("/api/users/me")
def get_current_user(current_user: UserDep) -> UserInfo:
    return UserInfo.from_user(current_user)

@app.get("/api/users/find-by-id/{userid}")
def read_user(userid: str, session: SessionDep, current_user: UserDep) -> UserInfo:
    user = session.exec(select(User).where(User.userid == userid)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInfo.from_user(user)

@app.delete("/api/users/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}

@app.post("/api/users/reset-password")
#TBD
def reset_password(user_request: CreateUserRequest, session: SessionDep) -> dict[str, str]:
    user = session.exec(select(User).where(User.email == user_request.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.passwordhash = hash_password(user_request.password)

@app.get("/api/users/find-by-name")
def find_user_by_name(username: str, session: SessionDep) -> UserInfo:
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInfo.from_user(user)

@app.post("/api/user/add-friend/{user_id}", status_code=201)
async def add_friend(user_id: str, session: SessionDep, current_user: UserDep):
    if user_id == current_user.userid:
        raise HTTPException(status_code=400, detail="Cannot add yourself as a friend")

    friend = session.exec(select(User).where(User.userid == user_id)).first()
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")

    friend_entry = session.exec(
        select(FriendListEntry)
        .where(
            ((FriendListEntry.user_id == friend.id) & (FriendListEntry.friend_id == current_user.id)) |
            ((FriendListEntry.friend_id == friend.id) & (FriendListEntry.user_id == current_user.id))
        )
    ).first()

    if not friend_entry:
        friend_entry = FriendListEntry(user_id=current_user.id, friend_id=friend.id)
        session.add(friend_entry)
        session.commit()
        await manager.broadcast_to_user(
            current_user.userid,
            "friend-state-update",
            FriendStateUpdate(other_user=UserInfo.from_user(friend), new_state="request-outgoing")
        )
        await manager.broadcast_to_user(
            friend.userid,
            "friend-state-update",
            FriendStateUpdate(other_user=UserInfo.from_user(current_user), new_state="request-incoming")
        )
        return {"message": "Friend request sent"}

    if friend_entry.pending:
        if friend_entry.friend_id == current_user.id:
            friend_entry.pending = False
            friend_entry.date_added = int(time.time())
            session.commit()

            await manager.broadcast_to_user(
                current_user.userid,
                "friend-state-update",
                FriendStateUpdate(other_user=UserInfo.from_user(friend), new_state="accept-incoming")
            )
            await manager.broadcast_to_user(
                friend.userid,
                "friend-state-update",
                FriendStateUpdate(other_user=UserInfo.from_user(current_user), new_state="accept-outgoing")
            )
            return {"message": "Friend request accepted."}
        else:
            raise HTTPException(status_code=400, detail="Friend request already sent. Wait for the other user to accept your friend request.")
    else:
        raise HTTPException(status_code=400, detail="User already in friends")

@app.post("/api/user/remove-friend/{user_id}", status_code=204)
async def remove_friend(user_id: str, session: SessionDep, current_user: UserDep):
    friend = session.exec(select(User).where(User.userid == user_id)).first()
    if not friend:
        raise HTTPException(status_code=404, detail="User not found")
    entry = session.exec(
        select(FriendListEntry)
        .where(
            (
                (FriendListEntry.user_id == friend.id) & (FriendListEntry.friend_id == current_user.id)
            ) | (
                (FriendListEntry.friend_id == friend.id) & (FriendListEntry.user_id == current_user.id)
            )
        )
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="User not a friend")

    if entry.pending:
        is_outgoing = entry.friend_id == friend.id
        if is_outgoing:
            # current_user unsent a friend request
            state_user = "remove-outgoing"
            state_friend = "remove-incoming"

        else:
            # current_user rejected a friend request
            state_user = "remove-incoming"
            state_friend = "remove-outgoing"

        await manager.broadcast_to_user(
            current_user.userid,
            "friend-state-update",
             FriendStateUpdate(other_user=UserInfo.from_user(friend), new_state=state_user)
        )
        await manager.broadcast_to_user(
            friend.userid,
            "friend-state-update",
             FriendStateUpdate(other_user=UserInfo.from_user(current_user), new_state=state_friend)
        )

    else:

        await manager.broadcast_to_user(
            current_user.userid,
            "friend-state-update",
             FriendStateUpdate(other_user=UserInfo.from_user(friend), new_state="remove-friend")
        )
        await manager.broadcast_to_user(
            friend.userid,
            "friend-state-update",
             FriendStateUpdate(other_user=UserInfo.from_user(current_user), new_state="remove-friend")
        )

    session.delete(entry)
    session.commit()
    return Response(status_code=204)


def get_friend_list_entries(session: SessionDep, user: User, what: str):
    if what == "friends":
        condition = ((FriendListEntry.user_id == user.id) | (FriendListEntry.friend_id == user.id)) & (FriendListEntry.pending == False)
        onclause =  (((User.id == FriendListEntry.friend_id) & (FriendListEntry.user_id == user.id)) |
                     ((User.id == FriendListEntry.user_id) & (FriendListEntry.friend_id == user.id)))
    elif what == "outgoing-requests":
        condition = (FriendListEntry.user_id == user.id) & (FriendListEntry.pending == True)
        onclause = (User.id == FriendListEntry.friend_id)
    elif what == "incoming-requests":
        condition = (FriendListEntry.friend_id == user.id) & (FriendListEntry.pending == True)
        onclause = (User.id == FriendListEntry.user_id)

    return session.exec(
        select(User)
        .join(FriendListEntry, onclause)
        .where(condition)
    ).all()

@app.get("/api/user/get-friends")
def get_friends(session: SessionDep, current_user: UserDep) -> list[UserInfo]:
    return [UserInfo.from_user(friend) for friend in get_friend_list_entries(session, current_user, "friends")]

@app.get("/api/user/outgoing-friend-requests")
def get_friends(session: SessionDep, current_user: UserDep) -> list[UserInfo]:
    return [UserInfo.from_user(friend) for friend in get_friend_list_entries(session, current_user, "outgoing-requests")]

@app.get("/api/user/incoming-friend-requests")
def get_friends(session: SessionDep, current_user: UserDep) -> list[UserInfo]:
    return [UserInfo.from_user(friend) for friend in get_friend_list_entries(session, current_user, "incoming-requests")]


@app.post("/api/message/{channel_id}")
async def post_message(new_message: NewMessage, channel_id: str, current_user: UserDep,
                       session: SessionDep):
    channel = session.exec(select(Channel).where(Channel.channel_id == channel_id)).first()
    if not channel:
        raise HTTPException(status_code=404, detail="User not found")
    timestamp = int(time.time())
    channel.last_update = timestamp
    message = Message(channel_id = channel.channel_id, sender_id = current_user.userid,
                      message=new_message.message, created_at=timestamp)
    session.add(message)
    session.commit()
    session.refresh(message)

    await manager.broadcast_to_channel(session, channel, "message", message, current_user)
    return message

@app.get("/api/messages/{channel_id}")
async def get_messages(channel_id: str, current_user: UserDep, session: SessionDep, limit: int = 5):
    channel = session.exec(select(Channel).where(Channel.channel_id == channel_id)).first()
    if not channel:
        raise HTTPException(status_code=404, detail="User not found")
    return list(session.exec(
        select(Message).where(Message.channel_id == channel.channel_id)
        .order_by(Message.id.desc()).limit(limit)
    ))[::-1]

@app.get("/api/opened_chat/all")
async def get_opened_chats(current_user:UserDep, session: SessionDep) -> list[OpenedChatResponse]:
    channels = session.exec(
        select(Channel)
        .join(OpenedChat, Channel.channel_id == OpenedChat.channel_id)
        .where(OpenedChat.user_id == current_user.userid)
    ).all()

    unread_messages_count_query=text(
    '''
        SELECT COUNT(*) AS count, messages.channel_id
        FROM messages
        JOIN channel_users ON messages.channel_id = channel_users.channel_id
        WHERE channel_users.user_id = :userid AND
        channel_users.last_read_message_id < messages.id
        GROUP BY messages.channel_id;
    ''').params(userid = str(current_user.userid))

    unread_messages_result = session.exec(unread_messages_count_query).all()
    unread_messages_dict = {row.channel_id: row.count for row in unread_messages_result}

    return [
        OpenedChatResponse(channel = channel, users=[
            UserInfo.from_user(user)
            for user in channel.get_users(session, current_user)
        ], unread_count=unread_messages_dict.get(str(channel.channel_id), 0))
        for channel in channels
    ]


class OpenChatOpenMode(str, Enum):
    user = "user"
    channel = "channel"

@app.post("/api/opened_chat/{open_mode}/{target_id}")
async def post_opened_chat(open_mode: OpenChatOpenMode, target_id: str, current_user:
UserDep, session: SessionDep) -> OpenedChatResponse:
    if open_mode == OpenChatOpenMode.user:
        user = session.exec(select(User).where(User.userid == target_id)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        channel = ChannelUser.find_user_channel(session, current_user.userid, user.userid)
        if not channel:
            # TODO add friend check

            channel = Channel(channel_type="user", last_update=int(time.time()))
            session.add(channel)
            session.add(ChannelUser(channel_id=channel.channel_id, user_id=current_user.userid))
            session.add(ChannelUser(channel_id=channel.channel_id, user_id=user.userid))

            print("created channel", channel)


    elif open_mode == OpenChatOpenMode.channel:
        channel = session.exec(select(Channel).where(Channel.channel_id == target_id)).first()
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")

    if not session.exec(select(OpenedChat).where((OpenedChat.user_id == current_user.userid) & (
            OpenedChat.channel_id == channel.channel_id))).first():
        opened_chat = OpenedChat(user_id=current_user.userid, channel_id=channel.channel_id)
        session.add(opened_chat)
        print("commit()")
        session.commit()
        print("refresh()", channel, channel.channel_id, channel.channel_type)
        session.refresh(channel)
        return OpenedChatResponse(channel = channel, users=[
            UserInfo.from_user(user)
            for user in channel.get_users(session, current_user)
        ], unread_count=0)
    else:
        raise HTTPException(status_code=400, detail="Chat already exists")

@app.delete("/api/opened_chat/{channel_id}")
async def delete_opened_chat(channel_id: str, current_user: UserDep, session: SessionDep):
    channel = session.exec(select(Channel).where(Channel.channel_id == channel_id)).first()
    if not channel:
        raise HTTPException(status_code=404, detail="User not found")
    if channel.channel_type == ChannelType.user:
        delete_chat = session.exec(select(OpenedChat).where(
            (OpenedChat.user_id == current_user.userid) & (OpenedChat.channel_id == channel_id)
        )).first()

        if delete_chat:
            session.delete(delete_chat)
            session.commit()
            return Response(status_code=204)
        else:
            raise HTTPException(status_code=404, detail="Chat not found")