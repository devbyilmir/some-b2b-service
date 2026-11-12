from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import EmailAlreadyExists, UsernameAlreadyExists

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
            constraint = e.orig.constraint_name

            if constraint == "users_email_key":
                raise EmailAlreadyExists from e

            if constraint == "users_username_key":
                raise UsernameAlreadyExists from e

        raise