import time
from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator
from contextlib import asynccontextmanager
from redis.asyncio import Redis
import os

from app.routers.user import router
from app.database import check_connection, engine
from app.middleware import ASGITimingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    await check_connection()

    redis = Redis.from_url(
        os.getenv("REDIS_URL"),
        decode_responses=True,
        max_connections=20,
        socket_connect_timeout=2,
        socket_timeout=2,
    )

    app.state.redis = redis

    yield

    await redis.aclose()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

Instrumentator().instrument(app).expose(app)

@app.middleware('http')
async def timing_middleware(request: Request, call_next):
    start = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start
    response.headers["X-Function-Process-Time"] = str(process_time)

    print(f"Function middleware: {process_time:.6f} sec")

    return response

app.include_router(router)
app.add_middleware(ASGITimingMiddleware)
