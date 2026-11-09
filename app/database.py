import asyncpg
from dotenv import load_dotenv
import os
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

load_dotenv()


DATABASE_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    # port=os.getenv("DB_PORT", 5432),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME"),
)

print(DATABASE_URL.render_as_string(hide_password=True))

engine = create_async_engine(
    DATABASE_URL,
    echo=True
    )

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def check_connection():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT version()"))
        print(result.scalar_one())


async def get_db():
    async with SessionLocal() as session:
        yield session


