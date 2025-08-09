#!/usr/bin/env python3
"""
FreelanceX.AI Auth + Memory API (local dev)
- JWT auth (bcrypt)
- SQLite via SQLAlchemy async
- Per-user chat history endpoints
"""

import os
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
import jwt
import sqlalchemy as sa
from sqlalchemy import Column, String, Boolean, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import declarative_base
import uuid

# Config
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALG = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = os.getenv("AUTH_DATABASE_URL", "sqlite+aiosqlite:///./auth_mem.db")

# DB setup
engine = create_async_engine(DATABASE_URL, future=True, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=False), server_default=sa.text("CURRENT_TIMESTAMP"))

class Chat(Base):
    __tablename__ = "chats"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), server_default=sa.text("CURRENT_TIMESTAMP"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI(title="FreelanceX.AI Auth+Memory API", version="0.1.0")

# Pydantic
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: int

class ChatItem(BaseModel):
    role: str
    content: str
    created_at: Optional[datetime] = None

# Utils
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: str, minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES):
    now = datetime.utcnow()
    exp = now + timedelta(minutes=minutes)
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG), int(exp.timestamp())

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/register", response_model=dict)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    q = await db.execute(sa.select(User).where(User.email == payload.email))
    existing = q.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=payload.email, password_hash=hash_password(payload.password), full_name=payload.full_name)
    db.add(user)
    await db.commit()
    return {"id": user.id, "email": user.email}

@app.post("/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    q = await db.execute(sa.select(User).where(User.email == form.username))
    user = q.scalar_one_or_none()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token, exp = create_access_token(user.id)
    return Token(access_token=token, expires_at=exp)

async def get_current_user(authorization: str = Header(None), db: AsyncSession = Depends(get_db)) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization")
    scheme, token = authorization.split()
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid auth scheme")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        sub = payload.get("sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    q = await db.execute(sa.select(User).where(User.id == sub))
    user = q.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/chat/save", response_model=dict)
async def save_chat(item: ChatItem, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    c = Chat(user_id=current_user.id, role=item.role, content=item.content)
    db.add(c)
    await db.commit()
    return {"id": c.id}

@app.get("/chat/history", response_model=List[ChatItem])
async def get_chat_history(limit: int = 50, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    q = await db.execute(
        sa.select(Chat).where(Chat.user_id == current_user.id).order_by(Chat.created_at.desc()).limit(limit)
    )
    rows = q.scalars().all()
    return [ChatItem(role=r.role, content=r.content, created_at=r.created_at) for r in reversed(rows)]


