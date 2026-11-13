from typing import TYPE_CHECKING

from app.models.base import Base

from sqlalchemy import Boolean, Integer, String, true
from sqlalchemy.orm import mapped_column, Mapped, relationship


if TYPE_CHECKING:
    from app.models.order import Order


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
        server_default=true(),
        nullable=False,
    )

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user"
    )
