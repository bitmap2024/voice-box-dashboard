from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user, require_super_admin
from app.db.session import get_db
from app.repositories import factories as factory_repo
from app.schemas import FactoryCreate

router = APIRouter()


@router.get("")
def list_factories(user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    rows = factory_repo.list_factories(db)
    if user["role_code"] == "super_admin":
        return rows
    return [item for item in rows if item["id"] == user["factory_id"]]


@router.post("")
def create_factory(payload: FactoryCreate, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    require_super_admin(user)
    return factory_repo.create_factory(db, name=payload.name, industry=payload.industry, plan_type=payload.plan_type)


@router.patch("/{factory_id}")
def update_factory(factory_id: str, payload: dict[str, Any], user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    require_super_admin(user)
    row = factory_repo.update_factory(db, factory_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="Factory not found")
    return row
