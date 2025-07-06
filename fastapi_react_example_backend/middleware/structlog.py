from __future__ import annotations

import time

from typing import TYPE_CHECKING
from typing import Any
from typing import TypedDict

import structlog

from asgi_correlation_id import correlation_id  # TODO: Check why it is not working
from starlette.responses import JSONResponse
from uvicorn.protocols.utils import get_path_with_query_string


if TYPE_CHECKING:
    from starlette.types import ASGIApp
    from starlette.types import Receive
    from starlette.types import Scope
    from starlette.types import Send


app_logger = structlog.get_logger("fastapi_react_example_backend")
access_logger = structlog.get_logger("fastapi_react_example_backend.access")


class AccessInfo(TypedDict, total=False):
    status_code: int
    start_time: float


class StructlogMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=correlation_id.get() or "-")

        info = AccessInfo()

        # Inner send function
        async def inner_send(message: Any) -> None:
            if message["type"] == "http.response.start":
                info["status_code"] = message["status"]
            await send(message)

        try:
            info["start_time"] = time.perf_counter_ns()
            await self.app(scope, receive, inner_send)
        except Exception as e:
            app_logger.exception(
                "An unhandled exception was caught by last resort middleware",
                exception_class=e.__class__.__name__,
                exc_info=e,
                stack_info=True,
            )
            info["status_code"] = 500
            response = JSONResponse(
                status_code=500,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred.",
                },
            )
            await response(scope, receive, send)
        finally:
            process_time = time.perf_counter_ns() - info["start_time"]
            client_host, client_port = scope["client"]
            http_method = scope["method"]
            http_version = scope["http_version"]
            url = get_path_with_query_string(scope)  # type: ignore[arg-type]

            access_logger.info(
                f"""{client_host}:{client_port} - "{http_method} {scope["path"]} HTTP/{http_version}" {info["status_code"]}""",
                http={
                    "url": str(url),
                    "status_code": info["status_code"],
                    "method": http_method,
                    "request_id": correlation_id.get() or "-",
                    "version": http_version,
                },
                network={"client": {"ip": client_host, "port": client_port}},
                duration=f"{process_time / 1_000_000:.3f} ms",
                process_time_ns=process_time,
            )
