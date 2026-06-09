import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.models.character import PromptVersion
from app.models.conversation import Conversation, ConversationTurn, LatencyTrace
from app.models.end_user import EndUser
from app.models.tenant import Factory
from app.repositories.helpers import enum_value, isoformat, to_str


def _trace_map_for_turns(db: Session, turn_ids: list[uuid.UUID]) -> dict[uuid.UUID, LatencyTrace]:
    if not turn_ids:
        return {}
    traces = db.query(LatencyTrace).filter(LatencyTrace.conversation_turn_id.in_(turn_ids)).all()
    return {t.conversation_turn_id: t for t in traces}


def build_llm_context(turns: list[ConversationTurn], current_index: int, system_prompt: str | None = None) -> str:
    lines: list[str] = []
    if system_prompt:
        lines.append(f"[system]\n{system_prompt}")
    for turn in turns[:current_index]:
        if turn.user_asr_text:
            lines.append(f"[user]\n{turn.user_asr_text}")
        if turn.ai_reply_text:
            lines.append(f"[assistant]\n{turn.ai_reply_text}")
    current = turns[current_index]
    if current.user_asr_text:
        lines.append(f"[user]\n{current.user_asr_text}")
    return "\n\n".join(lines)


def turn_to_dict(
    turn: ConversationTurn,
    trace: LatencyTrace | None = None,
    *,
    llm_context: str | None = None,
) -> dict[str, Any]:
    e2e = trace.e2e_first_response_ms if trace else turn.latency_total_ms
    payload = {
        "id": to_str(turn.id),
        "factory_id": to_str(turn.factory_id),
        "conversation_id": to_str(turn.conversation_id),
        "device_id": to_str(turn.device_id),
        "character_id": to_str(turn.character_id),
        "trace_id": turn.trace_id,
        "user_asr_text": turn.user_asr_text,
        "ai_reply_text": turn.ai_reply_text,
        "intent": turn.intent,
        "fallback_hit": turn.fallback_hit,
        "safety_hit": turn.safety_hit,
        "success": turn.success,
        "error_code": turn.error_code,
        "latency_total_ms": turn.latency_total_ms,
        "e2e_first_response_ms": e2e,
        "created_at": isoformat(turn.created_at),
    }
    if llm_context is not None:
        payload["llm_context"] = llm_context
    return payload


def conversation_to_dict(conv: Conversation, factory_name: str | None = None) -> dict[str, Any]:
    return {
        "id": to_str(conv.id),
        "factory_id": to_str(conv.factory_id),
        "factory_name": factory_name,
        "device_id": to_str(conv.device_id),
        "character_id": to_str(conv.character_id),
        "anonymous_session_id": conv.anonymous_session_id,
        "anonymous_user_label": conv.anonymous_user_label,
        "user_segment": conv.user_segment,
        "started_at": isoformat(conv.started_at),
        "ended_at": isoformat(conv.ended_at),
        "total_turns": conv.total_turns,
        "success": conv.success,
        "total_latency_ms": conv.total_latency_ms,
        "feedback": conv.feedback,
    }


def trace_to_dict(trace: LatencyTrace) -> dict[str, Any]:
    return {
        "vad_ms": trace.vad_ms,
        "upload_ms": trace.upload_ms,
        "asr_ms": trace.asr_ms,
        "llm_ttft_ms": trace.llm_ttft_ms,
        "llm_total_ms": trace.llm_total_ms,
        "tts_first_audio_ms": trace.tts_first_audio_ms,
        "tts_total_ms": trace.tts_total_ms,
        "playback_start_ms": trace.playback_start_ms,
        "e2e_first_response_ms": trace.e2e_first_response_ms,
    }


def _factory_name_map(db: Session, factory_ids: set[str] | None) -> dict[str, str]:
    query = db.query(Factory)
    if factory_ids:
        query = query.filter(Factory.id.in_([uuid.UUID(fid) for fid in factory_ids]))
    return {str(f.id): f.name for f in query.all()}


def list_conversations(db: Session, factory_ids: set[str] | None = None) -> list[dict[str, Any]]:
    result, _ = list_conversations_paginated(db, factory_ids, page=1, page_size=100000)
    return result


def list_conversations_paginated(
    db: Session,
    factory_ids: set[str] | None = None,
    *,
    page: int = 1,
    page_size: int = 50,
    keyword: str | None = None,
    status: str | None = None,
    device_id: str | None = None,
    end_user_id: str | None = None,
) -> tuple[list[dict[str, Any]], int]:
    query = db.query(Conversation)
    if factory_ids:
        query = query.filter(Conversation.factory_id.in_([uuid.UUID(fid) for fid in factory_ids]))
    if device_id:
        query = query.filter(Conversation.device_id == uuid.UUID(device_id))
    if end_user_id:
        end_user = db.get(EndUser, uuid.UUID(end_user_id))
        if end_user and end_user.device_id:
            query = query.filter(Conversation.device_id == end_user.device_id)
        else:
            return [], 0
    if status == "success":
        query = query.filter(Conversation.success.is_(True))
    elif status == "failed":
        query = query.filter(Conversation.success.is_(False))
    if keyword:
        kw = f"%{keyword}%"
        query = query.filter(
            (Conversation.anonymous_user_label.ilike(kw))
            | (Conversation.anonymous_session_id.ilike(kw))
            | (Conversation.user_segment.ilike(kw))
        )
    total = query.count()
    names = _factory_name_map(db, factory_ids)
    rows = (
        query.order_by(Conversation.started_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return [conversation_to_dict(c, names.get(str(c.factory_id))) for c in rows], total


def get_conversation(db: Session, conversation_id: str) -> dict[str, Any] | None:
    conv = db.get(Conversation, uuid.UUID(conversation_id))
    if not conv:
        return None
    factory = db.get(Factory, conv.factory_id)
    turns = (
        db.query(ConversationTurn)
        .filter(ConversationTurn.conversation_id == conv.id)
        .order_by(ConversationTurn.created_at)
        .all()
    )
    trace_map = _trace_map_for_turns(db, [t.id for t in turns])
    prompt_cache: dict[str, str] = {}

    def system_prompt_for(turn: ConversationTurn) -> str | None:
        if not turn.prompt_version_id:
            return None
        key = str(turn.prompt_version_id)
        if key not in prompt_cache:
            version = db.get(PromptVersion, turn.prompt_version_id)
            prompt_cache[key] = version.system_prompt if version else ""
        return prompt_cache[key] or None

    return conversation_to_dict(conv, factory.name if factory else None) | {
        "turns": [
            turn_to_dict(
                t,
                trace_map.get(t.id),
                llm_context=build_llm_context(turns, idx, system_prompt_for(t)),
            )
            for idx, t in enumerate(turns)
        ]
    }


def list_conversations_by_device(db: Session, device_id: str, factory_ids: set[str] | None = None) -> list[dict[str, Any]]:
    query = db.query(Conversation).filter(Conversation.device_id == uuid.UUID(device_id))
    if factory_ids:
        query = query.filter(Conversation.factory_id.in_([uuid.UUID(fid) for fid in factory_ids]))
    names = _factory_name_map(db, factory_ids)
    return [
        conversation_to_dict(c, names.get(str(c.factory_id)))
        for c in query.order_by(Conversation.started_at.desc()).all()
    ]


def list_turns(db: Session, factory_ids: set[str] | None = None) -> list[dict[str, Any]]:
    query = db.query(ConversationTurn)
    if factory_ids:
        query = query.filter(ConversationTurn.factory_id.in_([uuid.UUID(fid) for fid in factory_ids]))
    turns = query.order_by(ConversationTurn.created_at.desc()).all()
    trace_map = _trace_map_for_turns(db, [t.id for t in turns])
    return [turn_to_dict(t, trace_map.get(t.id)) for t in turns]


def get_turn_trace(db: Session, turn_id: str) -> dict[str, Any] | None:
    turn = db.get(ConversationTurn, uuid.UUID(turn_id))
    if not turn:
        return None
    trace = db.query(LatencyTrace).filter(LatencyTrace.conversation_turn_id == turn.id).first()
    turns = (
        db.query(ConversationTurn)
        .filter(ConversationTurn.conversation_id == turn.conversation_id)
        .order_by(ConversationTurn.created_at)
        .all()
    )
    current_index = next((idx for idx, item in enumerate(turns) if item.id == turn.id), 0)
    system_prompt = None
    if turn.prompt_version_id:
        version = db.get(PromptVersion, turn.prompt_version_id)
        system_prompt = version.system_prompt if version else None
    llm_context = build_llm_context(turns, current_index, system_prompt)
    return {
        "turn": turn_to_dict(turn, trace, llm_context=llm_context),
        "trace": trace_to_dict(trace) if trace else {},
    }


def list_badcases(db: Session, factory_ids: set[str] | None = None) -> list[dict[str, Any]]:
    turns = list_turns(db, factory_ids)
    return [
        t | {"badcase_type": "ASR 低置信度" if t["error_code"] else "高延迟"}
        for t in turns
        if t["fallback_hit"] or not t["success"] or (t["latency_total_ms"] or 0) > 3000
    ]


def get_latency_traces(db: Session, factory_ids: set[str] | None = None) -> list[dict[str, Any]]:
    query = db.query(ConversationTurn, LatencyTrace).join(
        LatencyTrace, LatencyTrace.conversation_turn_id == ConversationTurn.id
    )
    if factory_ids:
        query = query.filter(ConversationTurn.factory_id.in_([uuid.UUID(fid) for fid in factory_ids]))
    results = []
    for turn, trace in query.all():
        results.append(
            trace_to_dict(trace)
            | {
                "turn_id": to_str(turn.id),
                "trace_id": turn.trace_id,
                "device_id": to_str(turn.device_id),
                "character_id": to_str(turn.character_id),
                "created_at": isoformat(turn.created_at),
            }
        )
    return results
