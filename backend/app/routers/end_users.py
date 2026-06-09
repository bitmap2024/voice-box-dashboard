from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, visible_factory_ids
from app.db.session import get_db
from app.repositories import end_users as end_user_repo

router = APIRouter()


def _get_end_user_or_404(db: Session, end_user_id: str, factory_ids: set[str]) -> dict:
    row = end_user_repo.get_end_user(db, end_user_id)
    if not row or row["factory_id"] not in factory_ids:
        raise HTTPException(status_code=404, detail="End user not found")
    return row


@router.get("")
def list_end_users(
    factory_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
    sn: str | None = None,
    user_id: str | None = None,
    keyword: str | None = None,
    user: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db, factory_id)
    rows, total = end_user_repo.list_end_users_paginated(
        db, factory_ids, page=page, page_size=page_size, sn=sn, user_id=user_id, keyword=keyword
    )
    return {"items": rows, "total": total, "page": page, "page_size": page_size}


@router.get("/{end_user_id}")
def get_end_user(
    end_user_id: str,
    factory_id: str | None = None,
    user: dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    factory_ids = visible_factory_ids(user, db, factory_id)
    return _get_end_user_or_404(db, end_user_id, factory_ids)
