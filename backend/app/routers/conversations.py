from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, visible_factory_ids
from app.core.time import utc_now
from app.db.session import get_db
from app.repositories import conversations as conversation_repo
from app.repositories import end_users as end_user_repo
from app.repositories.factories import list_factories
from app.services.enrichment import character_name, device_name

router = APIRouter()


def _enrich_conversation(db: Session, item: dict[str, Any], factory_names: dict[str, str]) -> dict[str, Any]:
    return item | {
        "device_sn": device_name(db, item["device_id"]),
        "character_name": character_name(db, item["character_id"]),
        "factory_name": item.get("factory_name") or factory_names.get(item["factory_id"]),
        "bound_user": end_user_repo.get_end_user_by_device(db, item["device_id"]),
    }


@router.get("/conversations")
def list_conversations(
    factory_id: str | None = None,
    page: int = 1,
    page_size: int = 50,
    keyword: str | None = None,
    status: str | None = None,
    device_id: str | None = None,
    end_user_id: str | None = None,
    user: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db, factory_id)
    factory_names = {f["id"]: f["name"] for f in list_factories(db)}
    rows, total = conversation_repo.list_conversations_paginated(
        db,
        factory_ids,
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=status,
        device_id=device_id,
        end_user_id=end_user_id,
    )
    return {
        "items": [_enrich_conversation(db, item, factory_names) for item in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db)
    row = conversation_repo.get_conversation(db, conversation_id)
    if not row or row["factory_id"] not in factory_ids:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return row | {
        "device_sn": device_name(db, row["device_id"]),
        "character_name": character_name(db, row["character_id"]),
        "bound_user": end_user_repo.get_end_user_by_device(db, row["device_id"]),
    }


@router.get("/conversation-turns/{turn_id}/trace")
def get_turn_trace(turn_id: str, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db)
    result = conversation_repo.get_turn_trace(db, turn_id)
    if not result or result["turn"]["factory_id"] not in factory_ids:
        raise HTTPException(status_code=404, detail="Turn not found")
    return result


@router.get("/badcases")
def list_badcases(factory_id: str | None = None, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    factory_ids = visible_factory_ids(user, db, factory_id)
    return [
        item | {"device_sn": device_name(db, item["device_id"]), "character_name": character_name(db, item["character_id"])}
        for item in conversation_repo.list_badcases(db, factory_ids)
    ]


@router.post("/badcases/{badcase_id}/mark")
def mark_badcase(badcase_id: str, payload: dict[str, Any], user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
    return {"id": badcase_id, "status": payload.get("status", "reviewed"), "marked_by": user["name"], "marked_at": utc_now().isoformat()}
