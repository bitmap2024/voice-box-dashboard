import uuid
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.time import utc_now
from app.models.character import AICharacter, PromptVersion
from app.models.conversation import Conversation, ConversationTurn
from app.models.device import Device
from app.repositories.helpers import enum_value, isoformat, to_str


def _character_stats(db: Session, character_id: uuid.UUID) -> dict[str, Any]:
    bound = db.query(func.count(Device.id)).filter(Device.current_character_id == character_id).scalar() or 0
    today_conv = (
        db.query(func.count(Conversation.id))
        .filter(Conversation.character_id == character_id, func.date(Conversation.started_at) == utc_now().date())
        .scalar()
        or 0
    )
    turns = db.query(ConversationTurn).filter(ConversationTurn.character_id == character_id).all()
    if turns:
        fallback_rate = sum(1 for t in turns if t.fallback_hit) / len(turns)
        latencies = [t.latency_total_ms for t in turns if t.latency_total_ms]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
    else:
        fallback_rate = 0
        avg_latency = 0
    return {
        "bound_device_count": bound,
        "today_conversations": today_conv,
        "fallback_rate": round(fallback_rate, 3),
        "avg_latency_ms": round(avg_latency),
    }


def character_to_dict(db: Session, character: AICharacter) -> dict[str, Any]:
    stats = _character_stats(db, character.id)
    return {
        "id": to_str(character.id),
        "factory_id": to_str(character.factory_id),
        "name": character.name,
        "scene_type": character.scene_type,
        "age_range": character.age_range,
        "tone_style": character.tone_style,
        "description": character.description,
        "status": enum_value(character.status),
        "current_prompt_version_id": to_str(character.current_prompt_version_id),
        **stats,
    }


def prompt_version_to_dict(version: PromptVersion) -> dict[str, Any]:
    creator_name = version.creator.name if version.creator else "-"
    return {
        "id": to_str(version.id),
        "factory_id": to_str(version.factory_id),
        "character_id": to_str(version.character_id),
        "version": version.version,
        "system_prompt": version.system_prompt,
        "structured_config": version.structured_config or {},
        "change_note": version.change_note,
        "status": enum_value(version.status),
        "created_by": creator_name,
        "created_at": isoformat(version.created_at),
        "published_at": isoformat(version.published_at),
    }


def list_characters(db: Session, factory_ids: set[str] | None = None) -> list[dict[str, Any]]:
    query = db.query(AICharacter)
    if factory_ids:
        query = query.filter(AICharacter.factory_id.in_([uuid.UUID(fid) for fid in factory_ids]))
    return [character_to_dict(db, c) for c in query.order_by(AICharacter.created_at).all()]


def get_character(db: Session, character_id: str) -> AICharacter | None:
    return db.get(AICharacter, uuid.UUID(character_id))


def get_character_dict(db: Session, character_id: str, with_versions: bool = False) -> dict[str, Any] | None:
    character = get_character(db, character_id)
    if not character:
        return None
    data = character_to_dict(db, character)
    if with_versions:
        versions = list_prompt_versions(db, character_id)
        data["prompt_versions"] = versions
    return data


def create_character(db: Session, *, factory_id: str, name: str, scene_type: str, age_range: str, tone_style: str, description: str) -> dict[str, Any]:
    row = AICharacter(
        factory_id=uuid.UUID(factory_id),
        name=name,
        scene_type=scene_type,
        age_range=age_range,
        tone_style=tone_style,
        description=description,
        status="draft",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return character_to_dict(db, row)


def update_character(db: Session, character_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    row = get_character(db, character_id)
    if not row:
        return None
    for key in ("name", "scene_type", "age_range", "tone_style", "description", "status"):
        if key in payload:
            setattr(row, key, payload[key])
    db.commit()
    return character_to_dict(db, row)


def list_prompt_versions(db: Session, character_id: str) -> list[dict[str, Any]]:
    rows = (
        db.query(PromptVersion)
        .options(joinedload(PromptVersion.creator))
        .filter(PromptVersion.character_id == uuid.UUID(character_id))
        .order_by(PromptVersion.created_at.desc())
        .all()
    )
    return [prompt_version_to_dict(v) for v in rows]


def create_prompt_version(
    db: Session,
    *,
    character_id: str,
    version: str,
    system_prompt: str,
    structured_config: dict,
    change_note: str,
    created_by_id: str | None,
) -> dict[str, Any]:
    character = get_character(db, character_id)
    if not character:
        raise ValueError("Character not found")
    row = PromptVersion(
        factory_id=character.factory_id,
        character_id=character.id,
        version=version,
        system_prompt=system_prompt,
        structured_config=structured_config,
        change_note=change_note,
        status="draft",
        created_by=uuid.UUID(created_by_id) if created_by_id else None,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    row = db.query(PromptVersion).options(joinedload(PromptVersion.creator)).filter(PromptVersion.id == row.id).first()
    assert row is not None
    return prompt_version_to_dict(row)


def publish_prompt_version(db: Session, version_id: str) -> dict[str, Any] | None:
    version = db.get(PromptVersion, uuid.UUID(version_id))
    if not version:
        return None
    db.query(PromptVersion).filter(PromptVersion.character_id == version.character_id).update({"status": "archived"})
    version.status = "published"
    version.published_at = utc_now()
    character = get_character(db, str(version.character_id))
    if character:
        character.current_prompt_version_id = version.id
        character.status = "published"
    db.commit()
    version = db.query(PromptVersion).options(joinedload(PromptVersion.creator)).filter(PromptVersion.id == version.id).first()
    assert version is not None
    return prompt_version_to_dict(version)


def get_character_name(db: Session, character_id: str) -> str:
    character = get_character(db, character_id)
    return character.name if character else "-"
