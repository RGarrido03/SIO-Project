from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Awaitable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles

from repository.config.database import init_db
from repository.config.settings import settings
from repository.routers import router
from repository.utils.middleware import decrypt_request


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    await init_db()
    yield


app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    title="SIO Project - Repository",
    version="1.0.0",
    debug=not settings.PRODUCTION,
    docs_url=None if settings.PRODUCTION else "/docs",
    redoc_url=None if settings.PRODUCTION else "/redoc",
    openapi_url=None if settings.PRODUCTION else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def encryption_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.method not in ["GET", "DELETE"]:
        request = await decrypt_request(request)

    response = await call_next(request)
    return response


app.mount(settings.STATIC_PATH, StaticFiles(directory="static"), name="static")
app.include_router(router)
