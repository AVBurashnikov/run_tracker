from datetime import date

from sqlalchemy import Integer, String, Date, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    created_at: Mapped[date] = mapped_column(Date, server_default=func.now())

    def __repr__(self):
        return f"User({self.id=}, {self.email=}"