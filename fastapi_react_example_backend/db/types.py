from __future__ import annotations

from datetime import UTC
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP
from sqlalchemy import TypeDecorator


if TYPE_CHECKING:
    from sqlalchemy.engine import Dialect


SQLITE_DIALECT_NAME = "sqlite"


class AwareDatetime(TypeDecorator[datetime]):
    impl = TIMESTAMP(timezone=True)
    cache_ok = True

    def process_bind_param(
        self, value: datetime | None, dialect: Dialect
    ) -> datetime | None:
        if isinstance(value, datetime) and value.tzinfo is None:
            return value.astimezone(UTC)

        return value

    def process_result_value(
        self, value: datetime | None, dialect: Dialect
    ) -> datetime | None:
        if (
            dialect.name == SQLITE_DIALECT_NAME
            and isinstance(value, datetime)
            and value.tzinfo is None
        ):
            return value.replace(tzinfo=UTC)

        return value
