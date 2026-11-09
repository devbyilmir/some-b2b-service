from app.models.base import Base

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import mapped_column, Mapped


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        unique=True
    )
    
    email: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        unique=True
    )
    
    age: Mapped[int | None] = mapped_column(
        Integer, 
        nullable=True
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
