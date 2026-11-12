from sqlalchemy import Row, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.user import User



async def get_sum_amount(
    session: AsyncSession,
) -> list[Row]:
    stmt = (
        select(
            User.id, 
            User.username, 
            func.sum(Order.amount).label("sum_amount")
        )
        .join(Order, User.id == Order.user_id)
        .group_by(User.id, User.username)
        .having(func.sum(Order.amount) > 20000)
        .order_by(func.sum(Order.amount).desc())
    )
    result = await session.execute(stmt)

    return result.all()


async def get_user_orders(
        session: AsyncSession,
        user_id: int,
) -> list[Row]:
    stmt = (
        select(Order)
        .where(Order.user_id == user_id)
    )

    result = await session.execute(stmt)
    
    return result.scalars().all()