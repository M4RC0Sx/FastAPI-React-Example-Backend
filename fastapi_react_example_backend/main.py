from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import structlog

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi_react_example_backend.api.v1.api import router as api_v1_router
from fastapi_react_example_backend.core.config import settings
from fastapi_react_example_backend.core.logging_config import setup_logging
from fastapi_react_example_backend.initial_data import init_db
from fastapi_react_example_backend.middleware.structlog import StructlogMiddleware


# TODO: Discord: dany_x8x

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    logger.info(f"Starting '{settings.PROJECT_NAME}' app...")
    await init_db()
    yield
    logger.info(f"Stopping '{settings.PROJECT_NAME}' app...")


app = FastAPI(lifespan=lifespan)
app.add_middleware(StructlogMiddleware)

if settings.BACKEND_CORS_ORIGINS:
    logger.info("CORS enabled!", cors_origins=settings.BACKEND_CORS_ORIGINS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

app.include_router(api_v1_router, prefix=settings.ROUTER_API_V1_PREFIX, tags=["v1"])


@app.get("/")
def read_root() -> dict[str, str]:
    return {"Hello": "World"}
