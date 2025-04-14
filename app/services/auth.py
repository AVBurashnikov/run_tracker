from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Security, Depends, HTTPException, status
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import get_db
from app.models.user import User


OAuth2FormDataDep = Annotated[OAuth2PasswordRequestForm, Depends()]
oauth2scheme = OAuth2PasswordBearer("/login/")

pwd_context = CryptContext(schemes=["bcrypt"])


def hash_pwd(pwd: str) -> str:
    return pwd_context.hash(pwd)


def pwd_verify(secret, hash_password) -> bool:
    return pwd_context.verify(secret, hash_password)


def get_current_user(token: str = Security(oauth2scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, settings.secret, settings.algorithm)
        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token.")

    user = db.scalar(select(User).filter_by(email=email))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def create_jwt_token(data: dict, expire_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expire_delta or timedelta(minutes=settings.expire_token_in_min))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, settings.algorithm)