from typing import Any

from fastapi import APIRouter, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.auth import create_token, get_current_user, public_user
from app.core.time import utc_now
from app.db.session import get_db
from app.repositories.users import authenticate_user, update_last_login
from app.schemas import LoginRequest

router = APIRouter()


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    user = authenticate_user(db, payload.account, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="账号或密码错误")
    token = create_token(str(user.id))
    update_last_login(db, str(user.id), utc_now())
    return {"token": token, "user": public_user({"id": str(user.id)}, db)}


@router.post("/logout")
def logout() -> dict[str, bool]:
    return {"ok": True}


@router.get("/me")
def me(user: dict[str, Any] = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, Any]:
    return public_user(user, db)
