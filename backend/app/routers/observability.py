from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, visible_factory_ids
from app.db.session import get_db
from app.repositories import conversations as conversation_repo
from app.services.enrichment import character_name, device_name

router = APIRouter()


@router.get("/latency")
def latency_observability(factory_id: str | None = None, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db, factory_id)
    traces = conversation_repo.get_latency_traces(db, factory_ids)
    traces = [
        t | {"device_sn": device_name(db, t["device_id"]), "character_name": character_name(db, t["character_id"])}
        for t in traces
    ]

    if not traces:
        return {"summary": [], "breakdown": [], "slow_traces": []}

    keys = ["vad_ms", "upload_ms", "asr_ms", "llm_ttft_ms", "llm_total_ms", "tts_first_audio_ms", "playback_start_ms", "e2e_first_response_ms"]
    breakdown = []
    for key in keys:
        values = [trace[key] for trace in traces if trace.get(key) is not None]
        if values:
            breakdown.append({"stage": key, "avg": round(sum(values) / len(values)), "p95": max(values)})

    return {
        "summary": [
            {"label": "E2E P95", "value": max(trace["e2e_first_response_ms"] for trace in traces), "unit": "ms", "status": "warning"},
            {"label": "ASR 平均", "value": round(sum(trace["asr_ms"] for trace in traces) / len(traces)), "unit": "ms", "status": "normal"},
            {"label": "LLM TTFT 平均", "value": round(sum(trace["llm_ttft_ms"] for trace in traces) / len(traces)), "unit": "ms", "status": "warning"},
            {"label": "TTS 首包平均", "value": round(sum(trace["tts_first_audio_ms"] for trace in traces) / len(traces)), "unit": "ms", "status": "normal"},
        ],
        "breakdown": breakdown,
        "slow_traces": sorted(traces, key=lambda item: item["e2e_first_response_ms"], reverse=True)[:8],
    }
