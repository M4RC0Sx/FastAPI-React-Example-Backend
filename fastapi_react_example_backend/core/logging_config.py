from __future__ import annotations

import logging

from logging.config import dictConfig
from typing import Any

import structlog

from fastapi_react_example_backend.core.config import settings


def setup_logging() -> None:
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    renderer: structlog.types.Processor
    if settings.ENVIRONMENT == "local":
        processors = [
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ]
        renderer = structlog.dev.ConsoleRenderer(colors=True)
        formatter = "console"

    else:
        processors = [
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.format_exc_info,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ]
        renderer = structlog.processors.JSONRenderer()
        formatter = "json"

    logging_config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": renderer,
            },
            "json": {
                "()": structlog.stdlib.ProcessorFormatter,
                "processor": renderer,
                "foreign_pre_chain": processors,
            },
        },
        "handlers": {
            "default": {
                "level": settings.LOG_LEVEL.upper(),
                "class": "logging.StreamHandler",
                "formatter": formatter,
            },
        },
        "loggers": {
            "": {
                "handlers": ["default"],
                "level": settings.LOG_LEVEL.upper(),
                "propagate": True,
            },
            "uvicorn.error": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

    dictConfig(logging_config)
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    for _log in ["uvircorn", "uvicorn.error", "uvicorn.access"]:
        logging.getLogger(_log).handlers.clear()
        logging.getLogger(_log).propagate = True

    logging.getLogger("uvicorn.access").handlers.clear()
    logging.getLogger("uvicorn.access").propagate = False
