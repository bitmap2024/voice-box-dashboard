import builtins
import uuid
from datetime import timedelta
from typing import Any

from sqlalchemy import func
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, visible_factory_ids
from app.core.time import utc_now
from app.db.session import get_db
from app.models.conversation import Conversation, ConversationTurn, LatencyTrace
from app.models.device import Device, DeviceTelemetry
from app.repositories import alerts as alert_repo
from app.repositories import conversations as conversation_repo
from app.repositories import devices as device_repo
from app.services.recommendations import build_recommendations

router = APIRouter()


@router.get("/overview")
def overview(factory_id: str | None = None, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db, factory_id)
    scoped_devices = device_repo.list_devices(db, factory_ids)
    turns = conversation_repo.list_turns(db, factory_ids)
    open_alerts = [item for item in alert_repo.list_alerts(db, factory_ids) if item["status"] == "open"]
    total = len(scoped_devices)
    online = len([item for item in scoped_devices if item["status"] == "online"])
    abnormal = len([item for item in scoped_devices if item["abnormal"]])
    e2e_values = [item["e2e_first_response_ms"] for item in turns if item.get("e2e_first_response_ms")] or [0]

    return {
        "kpis": [
            {"label": "当前在线设备", "value": online, "unit": f"/ {total}", "trend": "+2.4%"},
            {"label": "今日对话次数", "value": sum(item["today_conversations"] for item in scoped_devices), "unit": "次", "trend": "+11.8%"},
            {"label": "P95 首句延迟", "value": round(max(e2e_values) / 1000, 2), "unit": "s", "trend": "-0.3s"},
            {"label": "异常设备", "value": abnormal, "unit": "台", "trend": "-6"},
            {"label": "对话成功率", "value": 93.5, "unit": "%", "trend": "+1.2%"},
            {"label": "云端调用成本", "value": 286.7, "unit": "元", "trend": "+8.1%"},
        ],
        "health": {
            "online_rate": round(online / total * 100, 1) if total else 0,
            "success_rate": 93.5,
            "weak_network_devices": len([item for item in scoped_devices if item["wifi_rssi"] < -75]),
            "open_alerts": len(open_alerts),
        },
        "alerts": open_alerts[:5],
        "recommendations": build_recommendations(user),
    }


def _percentile(values: list[int], pct: float) -> float:
    if not values:
        return 0
    sorted_vals = sorted(values)
    index = min(len(sorted_vals) - 1, int(len(sorted_vals) * pct))
    return sorted_vals[index] / 1000


@router.get("/trends")
def trends(time_range: str = "7d", factory_id: str | None = None, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db, factory_id)
    days = 7 if time_range == "7d" else 24
    now = utc_now()
    labels = [(now - timedelta(days=days - index - 1)).strftime("%m-%d") for index in builtins.range(days)]
    uuid_ids = [uuid.UUID(fid) for fid in factory_ids] if factory_ids else None

    online_points = []
    conv_points = []
    latency_points = []
    failure_points = []

    for index, label in enumerate(labels):
        day_start = (now - timedelta(days=days - index - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)

        tel_query = db.query(func.count(func.distinct(DeviceTelemetry.device_id))).filter(
            DeviceTelemetry.ts >= day_start,
            DeviceTelemetry.ts < day_end,
            DeviceTelemetry.online.is_(True),
        )
        if uuid_ids:
            tel_query = tel_query.filter(DeviceTelemetry.factory_id.in_(uuid_ids))
        online_count = tel_query.scalar() or 0
        if online_count == 0:
            dev_query = db.query(func.count(Device.id)).filter(Device.status == "online")
            if uuid_ids:
                dev_query = dev_query.filter(Device.factory_id.in_(uuid_ids))
            online_count = dev_query.scalar() or 0

        conv_count = db.query(func.count(Conversation.id)).filter(
            Conversation.started_at >= day_start,
            Conversation.started_at < day_end,
        )
        if uuid_ids:
            conv_count = conv_count.filter(Conversation.factory_id.in_(uuid_ids))
        conv_total = conv_count.scalar() or 0

        trace_query = (
            db.query(LatencyTrace.e2e_first_response_ms)
            .join(ConversationTurn, LatencyTrace.conversation_turn_id == ConversationTurn.id)
            .filter(ConversationTurn.created_at >= day_start, ConversationTurn.created_at < day_end)
        )
        if uuid_ids:
            trace_query = trace_query.filter(ConversationTurn.factory_id.in_(uuid_ids))
        e2e_vals = [row[0] for row in trace_query.all() if row[0] is not None]

        fail_query = db.query(func.count(ConversationTurn.id)).filter(
            ConversationTurn.created_at >= day_start,
            ConversationTurn.created_at < day_end,
            ConversationTurn.success.is_(False),
        )
        if uuid_ids:
            fail_query = fail_query.filter(ConversationTurn.factory_id.in_(uuid_ids))
        fail_count = fail_query.scalar() or 0
        turn_total = db.query(func.count(ConversationTurn.id)).filter(
            ConversationTurn.created_at >= day_start,
            ConversationTurn.created_at < day_end,
        )
        if uuid_ids:
            turn_total = turn_total.filter(ConversationTurn.factory_id.in_(uuid_ids))
        turns = turn_total.scalar() or 1

        online_points.append({"label": label, "value": online_count})
        conv_points.append({"label": label, "value": conv_total})
        latency_points.append({
            "label": label,
            "p50": round(_percentile(e2e_vals, 0.5), 2) if e2e_vals else 1.1,
            "p95": round(_percentile(e2e_vals, 0.95), 2) if e2e_vals else 2.8,
        })
        failure_points.append({"label": label, "value": round(fail_count / max(turns, 1) * 100, 1)})

    return {
        "online": online_points,
        "conversations": conv_points,
        "latency": latency_points,
        "failure": failure_points,
    }


@router.get("/recommendations")
def recommendations(user: dict[str, Any] = Depends(get_current_user)) -> list[dict[str, Any]]:
    return build_recommendations(user)
