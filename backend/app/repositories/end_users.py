import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.end_user import EndUser
from app.models.tenant import Factory
from app.repositories.helpers import isoformat, to_str


def end_user_to_dict(user: EndUser, device: Device | None = None, factory: Factory | None = None) -> dict[str, Any]:
    return {
        "id": to_str(user.id),
        "factory_id": to_str(user.factory_id),
        "factory_name": factory.name if factory else None,
        "device_id": to_str(user.device_id),
        "device_sn": device.sn if device else None,
        "nickname": user.nickname,
        "age_range": user.age_range,
        "region": user.region,
        "user_segment": user.user_segment,
        "bound_at": isoformat(user.bound_at),
        "last_active_at": isoformat(user.last_active_at),
        "total_conversations": user.total_conversations,
        "created_at": isoformat(user.created_at),
    }


def get_end_user(db: Session, end_user_id: str) -> dict[str, Any] | None:
    row = db.get(EndUser, uuid.UUID(end_user_id))
    if not row:
        return None
    device = db.get(Device, row.device_id) if row.device_id else None
    factory = db.get(Factory, row.factory_id)
    return end_user_to_dict(row, device, factory)


def get_end_user_by_device(db: Session, device_id: str) -> dict[str, Any] | None:
    row = db.query(EndUser).filter(EndUser.device_id == uuid.UUID(device_id)).first()
    if not row:
        return None
    device = db.get(Device, row.device_id) if row.device_id else None
    factory = db.get(Factory, row.factory_id)
    return end_user_to_dict(row, device, factory)


def list_end_users(db: Session, factory_ids: set[str] | None = None) -> list[dict[str, Any]]:
    rows, _ = list_end_users_paginated(db, factory_ids, page=1, page_size=100000)
    return rows


def list_end_users_paginated(
    db: Session,
    factory_ids: set[str] | None = None,
    *,
    page: int = 1,
    page_size: int = 20,
    sn: str | None = None,
    user_id: str | None = None,
    keyword: str | None = None,
) -> tuple[list[dict[str, Any]], int]:
    query = db.query(EndUser, Device, Factory).outerjoin(Device, EndUser.device_id == Device.id).join(Factory, EndUser.factory_id == Factory.id)
    if factory_ids:
        query = query.filter(EndUser.factory_id.in_([uuid.UUID(fid) for fid in factory_ids]))
    if user_id:
        query = query.filter(EndUser.id == uuid.UUID(user_id))
    if sn:
        query = query.filter(Device.sn.ilike(f"%{sn}%"))
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter((EndUser.nickname.ilike(kw)) | (EndUser.user_segment.ilike(kw)) | (Device.sn.ilike(kw)))
    total = query.count()
    rows = (
        query.order_by(EndUser.last_active_at.desc().nullslast(), EndUser.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return [end_user_to_dict(user, device, factory) for user, device, factory in rows], total
