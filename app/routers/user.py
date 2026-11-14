import asyncio

from fastapi import BackgroundTasks, Depends, APIRouter, HTTPException

from app.core.exceptions import EmailAlreadyExists, UsernameAlreadyExists
from app.database import get_db

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.user import create_user_service
from app.schemas.user import UserCreate
from app.services.user import get_user_with_orders_s, get_user_with_orders_j

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_db),
):
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }


async def log_user_registration(user_id: int):
        await asyncio.sleep(5)
        print(f"user {user_id} just registered!")

@router.post("/")
async def create_user(
    data: UserCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
):
    try:
        user = await create_user_service(session, data)
        user_id = user.id

        await session.commit()

    except EmailAlreadyExists:
        raise HTTPException(
            status_code=409,
            detail="Такой email уже зарегистрирован",
        )
    except UsernameAlreadyExists:
        raise HTTPException(
            status_code=409,
            detail="Такой username уже занят",
        )

    background_tasks.add_task(log_user_registration, user_id)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }


@router.get("/test/selectinload")
async def test_selectinload(
    session: AsyncSession = Depends(get_db),
):
    users = await get_user_with_orders_s(session)

    return [
        {
            "id": user.id,
            "username": user.username,
            "orders_count": len(user.orders),
        }
        for user in users
    ]


@router.get("/test/joinedload")
async def test_joinedload(
    session: AsyncSession = Depends(get_db),
):
    users = await get_user_with_orders_j(session)

    return [
        {
            "id": user.id,
            "username": user.username,
            "orders_count": len(user.orders),
        }
        for user in users
    ]