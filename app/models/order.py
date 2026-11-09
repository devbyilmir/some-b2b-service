from app.models.base import Base

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )
    
    amount: Mapped[int] = mapped_column(
        Integer, 
        nullable=False,
    )
    
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

