from typing import Annotated

from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db, SessionDep
from app.models.user import User
from app.schemas.access_token import AccessTokenDTO
from app.schemas.user import UserReadDTO, UserWriteDTO
from app.services.auth import (
    hash_pwd,
    pwd_verify,
    create_jwt_token,
    OAuth2FormDataDep
)

router = APIRouter(tags=["Auth"])


@router.post(
    "/register/",
    response_model=UserReadDTO,
    status_code=status.HTTP_201_CREATED
)
def register(user: UserWriteDTO, db: SessionDep):
    existed_user = db.scalar(select(User).filter_by(email=user.email))
    if existed_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email already used.")
    hashed_password = hash_pwd(user.hashed_password)
    new_user = User(email=user.email, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login/", response_model=AccessTokenDTO)
def login(form_data: OAuth2FormDataDep, db: SessionDep):
    user = db.scalar(select(User).filter_by(email=form_data.username))
    if user is None or not pwd_verify(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials.")

    return {
        "access_token": create_jwt_token({"sub": user.email}),
        "token_type": "bearer"
    }
