import uuid
from datetime import datetime
from typing import Any


SEED_NAMESPACE = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def seed_uuid(key: str) -> uuid.UUID:
    return uuid.uuid5(SEED_NAMESPACE, key)


def to_str(value: uuid.UUID | str | None) -> str | None:
    if value is None:
        return None
    return str(value)


def isoformat(value: datetime | None) -> str | None:
    if value is None:
        return None
    return value.isoformat().replace("+00:00", "Z")


def enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value
