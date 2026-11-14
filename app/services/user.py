from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from app.core.exceptions import EmailAlreadyExists, UsernameAlreadyExists

from app.models.order import Order
from app.models.user import User

from app.schemas.user import UserCreate



async def create_user_service(
    session: AsyncSession,    
    data: UserCreate,
):
    try:
        user_dict = data.model_dump()
        
        user = User(**user_dict)

        session.add(user)
        
        await session.flush()

        return user
    
    except IntegrityError as e:
        await session.rollback()

        if e.orig.sqlstate == "23505":
            original_error = e.orig.__cause__

            constraint = (
                getattr(e.orig, "constraint_name", None)
                or getattr(original_error, "constraint_name", None)
            )

            if constraint == "users_email_key":
                raise EmailAlreadyExists from e

            if constraint == "users_username_key":
                raise UsernameAlreadyExists from e

        raise


async def get_user_with_orders(
    session: AsyncSession,
    user_id: int,
):
    stmt = (
        select(User)
        .options(selectinload(User.orders))
        .where(User.id == user_id)
    )

    result = await session.execute(stmt)
    
    return result.scalars().one_or_none()


async def get_user_with_orders_s(
    session: AsyncSession,
):
    stmt = (
        select(User)
        .options(selectinload(User.orders))
        .where(User.is_active.is_(True))
        .limit(100)
    )

    result = await session.execute(stmt)
    users = result.scalars().all()
    
    return users


async def get_user_with_orders_j(
    session: AsyncSession,
):
    stmt = (
        select(User)
        .options(joinedload(User.orders))
        .where(User.is_active.is_(True))
        .limit(100)
    )

    result = await session.execute(stmt)
    users = result.unique().scalars().all()
    
    return users


async def get_user_order_more_5000(
    session: AsyncSession
):
    stmt = (
        select(User)
        .options(
            selectinload(
                User.orders.and_(Order.amount > 5000)
            )
        )
        .where(
            User.is_active.is_(True),
            User.orders.any(Order.amount > 5000) 
        )
    )
    # stmt = stmt.execution_options(populate_existing=True)

    result = await session.execute(stmt)

    return result.scalars().all()