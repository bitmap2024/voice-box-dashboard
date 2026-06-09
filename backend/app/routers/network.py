from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, visible_factory_ids
from app.db.session import get_db
from app.repositories import alerts as alert_repo
from app.repositories import devices as device_repo

router = APIRouter()


@router.get("/summary")
def network_summary(factory_id: str | None = None, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db, factory_id)
    scoped_devices = device_repo.list_devices(db, factory_ids)
    scoped_alerts = alert_repo.list_alerts(db, factory_ids)
    weak_devices = [item for item in scoped_devices if item["wifi_rssi"] < -75]
    online_devices = [item for item in scoped_devices if item["status"] == "online"]

    firmware_stats: dict[str, dict] = {}
    batch_stats: dict[str, dict] = {}
    for item in scoped_devices:
        fw = item["firmware_version"]
        firmware_stats.setdefault(fw, {"device_count": 0, "abnormal": 0})
        firmware_stats[fw]["device_count"] += 1
        if item["abnormal"]:
            firmware_stats[fw]["abnormal"] += 1
        batch = item.get("batch_no") or "unknown"
        batch_stats.setdefault(batch, {"weak": 0, "total": 0})
        batch_stats[batch]["total"] += 1
        if item["wifi_rssi"] < -75:
            batch_stats[batch]["weak"] += 1

    return {
        "summary": [
            {"label": "在线率", "value": round(len(online_devices) / len(scoped_devices) * 100, 1) if scoped_devices else 0, "unit": "%"},
            {"label": "弱网设备", "value": len(weak_devices), "unit": "台"},
            {"label": "平均 RTT", "value": round(sum(item["rtt_ms"] for item in scoped_devices) / len(scoped_devices)) if scoped_devices else 0, "unit": "ms"},
            {"label": "未处理网络告警", "value": len([item for item in scoped_alerts if item["status"] == "open" and item["alert_type"] in {"weak_network", "offline"}]), "unit": "条"},
        ],
        "weak_rank": sorted(scoped_devices, key=lambda item: item["wifi_rssi"])[:10],
        "rtt_rank": sorted(scoped_devices, key=lambda item: item["rtt_ms"], reverse=True)[:10],
        "firmware_risk": [
            {"firmware": fw, "device_count": s["device_count"], "abnormal_rate": round(s["abnormal"] / s["device_count"] * 100, 1)}
            for fw, s in firmware_stats.items()
        ],
        "batch_risk": [
            {"batch_no": batch, "weak_rate": round(s["weak"] / s["total"] * 100, 1), "reconnect_rate": 7.4}
            for batch, s in batch_stats.items()
        ],
    }
