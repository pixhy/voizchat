import hashlib
import os
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, SQLModel, create_engine, select
from model.user import User, CreateUserRequest, PrivateUserInfo, LoginRequest, UserInfo
from model.friend_list import FriendListEntry
from base64 import b64encode, b64decode
import jwt
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
import time
from email_service import send_verification_email

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
    jwt_public_key = f'-----BEGIN PUBLIC KEY-----\n{jwt_public_key}\n-----END PUBLIC KEY-----\n'
else:
    with open("public_key.pem", "r") as public_file:
        jwt_public_key = public_file.read()

jwt_private_key = os.getenv("AUTH_JWT_PRIVKEY")
if jwt_private_key:
    jwt_private_key = f'-----BEGIN PRIVATE KEY-----\n{jwt_private_key}\n-----END PRIVATE KEY-----\n'
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
            raise credentials_exception
    except jwt.InvalidTokenError as e:
        raise credentials_exception
    user = session.get(User, user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if not current_user.is_verified:
        raise HTTPException(status_code=400, detail="Unverified user")
    return current_user

@app.post("/api/users/register")
def create_user(user_request: CreateUserRequest, session: SessionDep) -> dict[str, str]:
    user = User(email=user_request.email, username=user_request.username)
    user.passwordhash = hash_password(user_request.password)
    session.commit()
    user.verification_code = os.urandom(20).hex()
    user.verification_code_expiration = int(time.time()) + 60*60*24 #one day
    send_verification_email(user_request.email, user.verification_code)
    session.add(user)
    session.commit()
    session.refresh(user)
    one_week_in_seconds = 60*60*24*7
    expiration = int(time.time()) + one_week_in_seconds
    payload = {"uid": user.id, "exp": expiration}
    token = jwt.encode(payload, jwt_private_key, algorithm="EdDSA")
    return jsonable_encoder({"token": token})

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


@app.post("/api/users/login")
def login_user(user_request: LoginRequest, session: SessionDep):
    user = session.exec(select(User).where(User.email == user_request.email)).first()
    if not user or not verify_password_hash(user.passwordhash, user_request.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    one_week_in_seconds = 60*60*24*7
    expiration = int(time.time()) + one_week_in_seconds
    payload = {"uid": user.id, "exp": expiration}
    token = jwt.encode(payload, jwt_private_key, algorithm="EdDSA")
    return jsonable_encoder({"token": token, "user": UserInfo.from_user(user)})

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
def get_current_user(current_user: Annotated[User, Depends(get_current_active_user)]) -> UserInfo:
    return UserInfo.from_user(current_user)

@app.get("/api/users/find-by-id/{user_id}")
def read_user(user_id: int, session: SessionDep) -> UserInfo:
    user = session.get(User, user_id)
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
def add_friend(user_id: str, session: SessionDep, current_user: Annotated[User, Depends(get_current_active_user)]):
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
        return {"message": "Friend request sent"}

    if friend_entry.pending:
        if friend_entry.friend_id == current_user.id:
            friend_entry.pending = False
            friend_entry.date_added = int(time.time())
            session.commit()
            return {"message": "Friend request accepted."}
        else:
            raise HTTPException(status_code=400, detail="Friend request already sent. Wait for the other user to accept your friend request.")
    else:
        raise HTTPException(status_code=400, detail="User already in friends")

@app.post("/api/user/remove-friend/{user_id}", status_code=204)
def remove_friend(user_id: str, session: SessionDep, current_user: Annotated[User, Depends(get_current_active_user)]):
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
def get_friends(session: SessionDep, current_user: Annotated[User, Depends(get_current_active_user)]) -> list[UserInfo]:
    return [UserInfo.from_user(friend) for friend in get_friend_list_entries(session, current_user, "friends")]

@app.get("/api/user/outgoing-friend-requests")
def get_friends(session: SessionDep, current_user: Annotated[User, Depends(get_current_active_user)]) -> list[UserInfo]:
    return [UserInfo.from_user(friend) for friend in get_friend_list_entries(session, current_user, "outgoing-requests")]

@app.get("/api/user/incoming-friend-requests")
def get_friends(session: SessionDep, current_user: Annotated[User, Depends(get_current_active_user)]) -> list[UserInfo]:
    return [UserInfo.from_user(friend) for friend in get_friend_list_entries(session, current_user, "incoming-requests")]
