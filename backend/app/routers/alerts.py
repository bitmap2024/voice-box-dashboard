import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, visible_factory_ids
from app.db.session import get_db
from app.repositories import alerts as alert_repo
from app.services.enrichment import device_name

router = APIRouter()


@router.get("")
def list_alerts(status: str | None = None, factory_id: str | None = None, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    factory_ids = visible_factory_ids(user, db, factory_id)
    rows = alert_repo.list_alerts(db, factory_ids, status=status)
    return [item | {"device_sn": device_name(db, item["device_id"])} if item.get("device_id") else item for item in rows]


@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: str, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db)
    from app.models.alert import Alert

    existing = db.get(Alert, uuid.UUID(alert_id))
    if not existing or str(existing.factory_id) not in factory_ids:
        raise HTTPException(status_code=404, detail="Alert not found")
    row = alert_repo.resolve_alert(db, alert_id)
    if not row:
        raise HTTPException(status_code=404, detail="Alert not found")
    return row
