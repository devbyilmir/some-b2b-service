from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager

from app.routers.user import router
from app.database import check_connection, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_connection()

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(router)
