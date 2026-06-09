import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.models.alert import Alert
from app.repositories.helpers import enum_value, isoformat, to_str


def alert_to_dict(alert: Alert) -> dict[str, Any]:
    return {
        "id": to_str(alert.id),
        "factory_id": to_str(alert.factory_id),
        "device_id": to_str(alert.device_id),
        "alert_type": alert.alert_type,
        "severity": enum_value(alert.severity),
        "title": alert.title,
        "content": alert.content,
        "status": enum_value(alert.status),
        "created_at": isoformat(alert.created_at),
        "resolved_at": isoformat(alert.resolved_at),
    }


def list_alerts(db: Session, factory_ids: set[str] | None = None, status: str | None = None) -> list[dict[str, Any]]:
    query = db.query(Alert)
    if factory_ids:
        query = query.filter(Alert.factory_id.in_([uuid.UUID(fid) for fid in factory_ids]))
    if status:
        query = query.filter(Alert.status == status)
    return [alert_to_dict(a) for a in query.order_by(Alert.created_at.desc()).all()]


def list_alerts_by_device(db: Session, device_id: str, factory_ids: set[str] | None = None) -> list[dict[str, Any]]:
    query = db.query(Alert).filter(Alert.device_id == uuid.UUID(device_id))
    if factory_ids:
        query = query.filter(Alert.factory_id.in_([uuid.UUID(fid) for fid in factory_ids]))
    return [alert_to_dict(a) for a in query.order_by(Alert.created_at.desc()).all()]


def resolve_alert(db: Session, alert_id: str) -> dict[str, Any] | None:
    alert = db.get(Alert, uuid.UUID(alert_id))
    if not alert:
        return None
    alert.status = "resolved"
    alert.resolved_at = utc_now()
    db.commit()
    db.refresh(alert)
    return alert_to_dict(alert)
