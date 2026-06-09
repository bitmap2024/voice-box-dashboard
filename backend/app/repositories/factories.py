import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models.tenant import Factory
from app.repositories.helpers import enum_value, isoformat, to_str


def factory_to_dict(factory: Factory) -> dict[str, Any]:
    return {
        "id": to_str(factory.id),
        "name": factory.name,
        "industry": factory.industry,
        "status": enum_value(factory.status),
        "plan_type": factory.plan_type,
        "device_quota": factory.device_quota,
        "created_at": isoformat(factory.created_at),
    }


def list_factories(db: Session) -> list[dict[str, Any]]:
    return [factory_to_dict(row) for row in db.query(Factory).order_by(Factory.created_at).all()]


def get_factory(db: Session, factory_id: str | uuid.UUID) -> Factory | None:
    return db.get(Factory, uuid.UUID(str(factory_id)))


def create_factory(db: Session, *, name: str, industry: str, plan_type: str, device_quota: int = 1000) -> dict[str, Any]:
    row = Factory(name=name, industry=industry, status="active", plan_type=plan_type, device_quota=device_quota)
    db.add(row)
    db.commit()
    db.refresh(row)
    return factory_to_dict(row)


def update_factory(db: Session, factory_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    row = get_factory(db, factory_id)
    if not row:
        return None
    for key in ("name", "industry", "status", "plan_type", "device_quota"):
        if key in payload:
            setattr(row, key, payload[key])
    db.commit()
    db.refresh(row)
    return factory_to_dict(row)
