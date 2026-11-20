import asyncio
import json
from fastapi import BackgroundTasks, Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis.exceptions import RedisError

from app.core.redis import RedisDep
from app.core.exceptions import EmailAlreadyExists, UsernameAlreadyExists
from app.database import get_db
from app.models.user import User
from app.services.user import create_user_service, update_user_service
from app.schemas.user import UserCreate, UserUpdate
from app.services.user import get_user_with_orders_s, get_user_with_orders_j

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    redis: RedisDep,
    session: AsyncSession = Depends(get_db),
):
    cache_key = f"user:{user_id}"

    # 1. Пытаемся получить данные из Redis
    try:
        cached_user = await redis.get(cache_key)

        if cached_user is not None:
            return json.loads(cached_user)

    except RedisError:
        pass

    # 2. Cache miss — обращаемся к PostgreSQL
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }

    # 3. Сохраняем результат в Redis
    try:
        await redis.set(
            cache_key,
            json.dumps(user_data),
            ex=300,
        )
    except RedisError:
        pass

    return user_data

@router.patch("/{user_id}")
async def update_user(
    user_id: int,
    data: UserUpdate,
    redis: RedisDep,
    session: AsyncSession = Depends(get_db),
):
    user = await session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    update_data = data.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields to update",
        )

    if any(value is None for value in update_data.values()):
        raise HTTPException(
            status_code=422,
            detail="Fields cannot be null",
        )

    try:
        user = await update_user_service(user, data)

        await session.commit()

    except Exception:
        await session.rollback()
        raise

    # Инвалидируем кэш
    try:
        await redis.delete(f"user:{user_id}")
    except RedisError:
        print(f"WARNING: failed to invalidate cache for user:{user_id}")

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
