from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, visible_factory_ids
from app.db.session import get_db
from app.repositories import alerts as alert_repo
from app.repositories import characters as character_repo
from app.repositories import conversations as conversation_repo
from app.repositories import devices as device_repo
from app.repositories import end_users as end_user_repo
from app.schemas import DeviceBindRequest

router = APIRouter()


@router.get("")
def list_devices(
    keyword: str | None = None,
    status: str | None = None,
    factory_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
    user: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db, factory_id)
    rows = [
        row | {"bound_user": end_user_repo.get_end_user_by_device(db, row["id"])}
        for row in device_repo.list_devices(db, factory_ids, keyword=keyword, status=status)
    ]
    total = len(rows)
    start = (page - 1) * page_size
    return {"items": rows[start : start + page_size], "total": total, "page": page, "page_size": page_size}


@router.post("/bind")
def bind_device(payload: DeviceBindRequest, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    if user["role_code"] == "super_admin":
        raise HTTPException(status_code=400, detail="平台管理员请先选择具体工厂")
    return device_repo.create_device(
        db,
        factory_id=user["factory_id"],
        sn=payload.sn,
        mac_address=payload.mac_address,
        model=payload.model,
        firmware_version=payload.firmware_version,
        batch_no=payload.batch_no,
        character_id=payload.character_id,
    )


@router.get("/{device_id}")
def get_device(device_id: str, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db)
    row = device_repo.get_device_dict(db, device_id)
    if not row or row["factory_id"] not in factory_ids:
        raise HTTPException(status_code=404, detail="Device not found")
    character = character_repo.get_character_dict(db, row["current_character_id"]) if row.get("current_character_id") else None
    bound_user = end_user_repo.get_end_user_by_device(db, device_id)
    return row | {"character": character, "bound_user": bound_user}


@router.patch("/{device_id}")
def update_device(device_id: str, payload: dict[str, Any], user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db)
    existing = device_repo.get_device_dict(db, device_id)
    if not existing or existing["factory_id"] not in factory_ids:
        raise HTTPException(status_code=404, detail="Device not found")
    row = device_repo.update_device(db, device_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="Device not found")
    return row


@router.get("/{device_id}/telemetry")
def device_telemetry(device_id: str, range: str = "24h", user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    factory_ids = visible_factory_ids(user, db)
    existing = device_repo.get_device_dict(db, device_id)
    if not existing or existing["factory_id"] not in factory_ids:
        raise HTTPException(status_code=404, detail="Device not found")
    hours = 24 if range == "24h" else 24
    return device_repo.list_device_telemetry(db, device_id, hours=hours)


@router.get("/{device_id}/conversations")
def device_conversations(device_id: str, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    factory_ids = visible_factory_ids(user, db)
    return conversation_repo.list_conversations_by_device(db, device_id, factory_ids)


@router.get("/{device_id}/alerts")
def device_alerts(device_id: str, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    factory_ids = visible_factory_ids(user, db)
    return alert_repo.list_alerts_by_device(db, device_id, factory_ids)
