from typing import Any
from uuid import uuid4

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.factories import list_factories
from app.repositories.users import get_user_by_id as db_get_user_by_id
from app.repositories.users import public_user_dict, user_to_dict

TOKENS: dict[str, str] = {}


def create_token(user_id: str) -> str:
    token = f"token_{uuid4().hex}"
    TOKENS[token] = user_id
    return token


def get_current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)) -> dict[str, Any]:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.removeprefix("Bearer ").strip()
    user_id = TOKENS.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db_get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_to_dict(user)


def public_user(user: dict[str, Any], db: Session) -> dict[str, Any]:
    db_user = db_get_user_by_id(db, user["id"])
    if not db_user:
        return user
    return public_user_dict(db, db_user)


def visible_factory_ids(user: dict[str, Any], db: Session, factory_id: str | None = None) -> set[str]:
    all_factories = {f["id"] for f in list_factories(db)}
    if user["role_code"] == "super_admin":
        if factory_id:
            if factory_id not in all_factories:
                raise HTTPException(status_code=404, detail="Factory not found")
            return {factory_id}
        return all_factories
    fid = user.get("factory_id")
    if not fid:
        raise HTTPException(status_code=403, detail="No factory assigned")
    return {fid}


def require_super_admin(user: dict[str, Any]) -> None:
    if user["role_code"] != "super_admin":
        raise HTTPException(status_code=403, detail="Only super admin can perform this action")
