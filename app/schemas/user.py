from datetime import date

from app.schemas.base import BaseDTO


class UserDTO(BaseDTO):
    email: str


class UserReadDTO(UserDTO):
    id: int


class UserWriteDTO(UserDTO):
    hashed_password: str
