from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.repositories import users as user_repo
from app.schemas import AdminUserCreate

router = APIRouter()


@router.get("/roles")
def list_roles(user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    return user_repo.list_roles(db)


@router.get("/admin-users")
def list_admin_users(user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    if user["role_code"] == "super_admin":
        return user_repo.list_admin_users(db)
    return user_repo.list_admin_users(db, factory_id=user["factory_id"])


@router.post("/admin-users")
def create_admin_user(payload: AdminUserCreate, user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    factory_id = payload.factory_id if user["role_code"] == "super_admin" else user["factory_id"]
    return user_repo.create_admin_user(
        db,
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        role_code=payload.role_code,
        factory_id=factory_id,
    )


@router.patch("/admin-users/{user_id}")
def update_admin_user(user_id: str, payload: dict[str, Any], user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    target = user_repo.get_user_by_id(db, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if user["role_code"] != "super_admin" and str(target.factory_id) != user["factory_id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    row = user_repo.update_admin_user(db, user_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row
