from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable, Awaitable, Any

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles

from repository.config.database import init_db
from repository.config.settings import settings
from repository.routers import router
from repository.utils.middleware import (
    decrypt_request_body,
    decrypt_request_key,
    encrypt_response,
)


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
    (request, token) = await decrypt_request_key(request)
    await decrypt_request_body(request, token)
    response = await call_next(request)

    await encrypt_response(
        response, request.state, request.headers.get("Encryption") is not None
    )

    return response


app.mount(settings.STATIC_PATH, StaticFiles(directory="static"), name="static")
app.include_router(router)


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="SIO Project - Repository",
        version="1.0.0",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"]["OAuth2PasswordBearer"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore
