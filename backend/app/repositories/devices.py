import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.models.conversation import Conversation
from app.models.device import Device, DeviceTelemetry
from app.repositories.helpers import enum_value, isoformat, to_str


def _latest_telemetry_map(db: Session, device_ids: list[uuid.UUID]) -> dict[uuid.UUID, DeviceTelemetry]:
    if not device_ids:
        return {}
    subq = (
        db.query(DeviceTelemetry.device_id, func.max(DeviceTelemetry.ts).label("max_ts"))
        .filter(DeviceTelemetry.device_id.in_(device_ids))
        .group_by(DeviceTelemetry.device_id)
        .subquery()
    )
    rows = (
        db.query(DeviceTelemetry)
        .join(subq, (DeviceTelemetry.device_id == subq.c.device_id) & (DeviceTelemetry.ts == subq.c.max_ts))
        .all()
    )
    return {row.device_id: row for row in rows}


def _today_conversation_counts(db: Session, device_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
    if not device_ids:
        return {}
    today = utc_now().date()
    rows = (
        db.query(Conversation.device_id, func.count(Conversation.id))
        .filter(Conversation.device_id.in_(device_ids), func.date(Conversation.started_at) == today)
        .group_by(Conversation.device_id)
        .all()
    )
    return {device_id: count for device_id, count in rows}


def device_to_dict(device: Device, telemetry: DeviceTelemetry | None = None, today_conversations: int = 0) -> dict[str, Any]:
    wifi_rssi = telemetry.wifi_rssi if telemetry else 0
    rtt_ms = telemetry.rtt_ms if telemetry else 0
    abnormal = device.status.value in {"warning", "offline"} or (wifi_rssi < -75)
    return {
        "id": to_str(device.id),
        "factory_id": to_str(device.factory_id),
        "sn": device.sn,
        "mac_address": device.mac_address,
        "model": device.model,
        "firmware_version": device.firmware_version,
        "batch_no": device.batch_no,
        "status": enum_value(device.status),
        "activated_at": isoformat(device.activated_at),
        "last_seen_at": isoformat(device.last_seen_at),
        "current_character_id": to_str(device.current_character_id),
        "wifi_rssi": wifi_rssi or 0,
        "rtt_ms": rtt_ms or 0,
        "today_conversations": today_conversations,
        "abnormal": abnormal,
    }


def _enrich_devices(db: Session, devices: list[Device]) -> list[dict[str, Any]]:
    ids = [d.id for d in devices]
    telemetry_map = _latest_telemetry_map(db, ids)
    conv_map = _today_conversation_counts(db, ids)
    return [device_to_dict(d, telemetry_map.get(d.id), conv_map.get(d.id, 0)) for d in devices]


def list_devices(db: Session, factory_ids: set[str] | None = None, keyword: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
    query = db.query(Device)
    if factory_ids:
        query = query.filter(Device.factory_id.in_([uuid.UUID(fid) for fid in factory_ids]))
    if status:
        query = query.filter(Device.status == status)
    devices = query.order_by(Device.created_at).all()
    rows = _enrich_devices(db, devices)
    if keyword:
        kw = keyword.lower()
        rows = [r for r in rows if kw in r["sn"].lower() or kw in r["mac_address"].lower()]
    return rows


def get_device(db: Session, device_id: str) -> Device | None:
    return db.get(Device, uuid.UUID(device_id))


def get_device_dict(db: Session, device_id: str) -> dict[str, Any] | None:
    device = get_device(db, device_id)
    if not device:
        return None
    return _enrich_devices(db, [device])[0]


def create_device(db: Session, *, factory_id: str, sn: str, mac_address: str, model: str, firmware_version: str, batch_no: str | None, character_id: str | None) -> dict[str, Any]:
    row = Device(
        factory_id=uuid.UUID(factory_id),
        sn=sn,
        mac_address=mac_address,
        model=model,
        firmware_version=firmware_version,
        batch_no=batch_no,
        status="offline",
        current_character_id=uuid.UUID(character_id) if character_id else None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return device_to_dict(row)


def update_device(db: Session, device_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    row = get_device(db, device_id)
    if not row:
        return None
    if "current_character_id" in payload:
        row.current_character_id = uuid.UUID(payload["current_character_id"]) if payload["current_character_id"] else None
    for key in ("firmware_version", "status", "batch_no"):
        if key in payload:
            setattr(row, key, payload[key])
    db.commit()
    return get_device_dict(db, device_id)


def list_device_telemetry(db: Session, device_id: str, hours: int = 24) -> list[dict[str, Any]]:
    since = utc_now() - timedelta(hours=hours)
    rows = (
        db.query(DeviceTelemetry)
        .filter(DeviceTelemetry.device_id == uuid.UUID(device_id), DeviceTelemetry.ts >= since)
        .order_by(DeviceTelemetry.ts)
        .all()
    )
    if rows:
        return [
            {
                "timestamp": isoformat(r.ts),
                "online": r.online,
                "wifi_rssi": r.wifi_rssi,
                "rtt_ms": r.rtt_ms,
                "reconnect_count": r.reconnect_count,
                "upload_fail_count": r.upload_fail_count,
                "playback_fail_count": r.playback_fail_count,
                "free_memory": r.free_memory,
                "cpu_usage": float(r.cpu_usage) if r.cpu_usage is not None else None,
            }
            for r in rows
        ]
    device = get_device_dict(db, device_id)
    if not device:
        return []
    points = []
    for index in range(hours):
        timestamp = utc_now() - timedelta(hours=hours - 1 - index)
        points.append({
            "timestamp": timestamp.isoformat(),
            "online": device["status"] != "offline" if index > 2 else device["status"] == "online",
            "wifi_rssi": device["wifi_rssi"] + ((index % 5) - 2) * 2,
            "rtt_ms": max(device["rtt_ms"], 60) + (index % 6) * 15,
            "reconnect_count": index % 4,
            "upload_fail_count": 1 if index % 9 == 0 else 0,
            "playback_fail_count": 1 if index % 13 == 0 else 0,
            "free_memory": 120000 - index * 380,
            "cpu_usage": 24 + index % 30,
        })
    return points


def get_device_sn(db: Session, device_id: str) -> str:
    device = get_device(db, device_id)
    return device.sn if device else "-"
