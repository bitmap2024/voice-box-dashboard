import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, visible_factory_ids
from app.db.session import get_db
from app.repositories import characters as character_repo
from app.schemas import CharacterCreate, PromptVersionCreate

router = APIRouter()


@router.get("/characters")
def list_characters(factory_id: str | None = None, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    factory_ids = visible_factory_ids(user, db, factory_id)
    return character_repo.list_characters(db, factory_ids)


@router.post("/characters")
def create_character(payload: CharacterCreate, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    if user["role_code"] == "super_admin":
        raise HTTPException(status_code=400, detail="平台管理员请先选择具体工厂")
    return character_repo.create_character(
        db,
        factory_id=user["factory_id"],
        name=payload.name,
        scene_type=payload.scene_type,
        age_range=payload.age_range,
        tone_style=payload.tone_style,
        description=payload.description,
    )


@router.get("/characters/{character_id}")
def get_character(character_id: str, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db)
    row = character_repo.get_character_dict(db, character_id, with_versions=True)
    if not row or row["factory_id"] not in factory_ids:
        raise HTTPException(status_code=404, detail="Character not found")
    return row


@router.patch("/characters/{character_id}")
def update_character(character_id: str, payload: dict[str, Any], user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db)
    existing = character_repo.get_character_dict(db, character_id)
    if not existing or existing["factory_id"] not in factory_ids:
        raise HTTPException(status_code=404, detail="Character not found")
    row = character_repo.update_character(db, character_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="Character not found")
    return row


@router.get("/characters/{character_id}/prompt-versions")
def list_prompt_versions(character_id: str, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    factory_ids = visible_factory_ids(user, db)
    existing = character_repo.get_character_dict(db, character_id)
    if not existing or existing["factory_id"] not in factory_ids:
        raise HTTPException(status_code=404, detail="Character not found")
    return character_repo.list_prompt_versions(db, character_id)


@router.post("/characters/{character_id}/prompt-versions")
def create_prompt_version(character_id: str, payload: PromptVersionCreate, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db)
    existing = character_repo.get_character_dict(db, character_id)
    if not existing or existing["factory_id"] not in factory_ids:
        raise HTTPException(status_code=404, detail="Character not found")
    return character_repo.create_prompt_version(
        db,
        character_id=character_id,
        version=payload.version,
        system_prompt=payload.system_prompt,
        structured_config=payload.structured_config,
        change_note=payload.change_note,
        created_by_id=user["id"],
    )


@router.post("/prompt-versions/{version_id}/publish")
def publish_prompt(version_id: str, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    return _publish_version(version_id, user, db)


@router.post("/prompt-versions/{version_id}/rollback")
def rollback_prompt(version_id: str, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    return _publish_version(version_id, user, db)


def _publish_version(version_id: str, user: dict[str, Any], db: Session) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db)
    from app.models.character import PromptVersion

    version = db.get(PromptVersion, uuid.UUID(version_id))
    if not version or str(version.factory_id) not in factory_ids:
        raise HTTPException(status_code=404, detail="Prompt version not found")
    row = character_repo.publish_prompt_version(db, version_id)
    if not row:
        raise HTTPException(status_code=404, detail="Prompt version not found")
    return row
