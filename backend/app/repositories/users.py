import uuid
from typing import Any

from sqlalchemy.orm import Session, joinedload

from app.core.security import hash_password
from app.models.tenant import AdminUser, Factory, Permission, Role
from app.repositories.factories import factory_to_dict
from app.repositories.helpers import enum_value, isoformat, to_str


def role_to_dict(role: Role, permissions: list[str] | None = None) -> dict[str, Any]:
    perm_codes = permissions
    if perm_codes is None:
        perm_codes = [item.code for item in role.permissions]
    return {
        "id": to_str(role.id),
        "name": role.name,
        "code": role.code,
        "permissions": perm_codes,
    }


def user_to_dict(user: AdminUser, *, include_password: bool = False) -> dict[str, Any]:
    data = {
        "id": to_str(user.id),
        "factory_id": to_str(user.factory_id),
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role_code": user.role.code,
        "status": enum_value(user.status),
        "last_login_at": isoformat(user.last_login_at),
    }
    if include_password:
        data["password"] = ""
    return data


def public_user_dict(db: Session, user: AdminUser) -> dict[str, Any]:
    role = role_to_dict(user.role)
    factory = factory_to_dict(user.factory) if user.factory else None
    return user_to_dict(user) | {"role": role, "factory": factory}


def list_roles(db: Session) -> list[dict[str, Any]]:
    roles = db.query(Role).options(joinedload(Role.permissions)).order_by(Role.code).all()
    return [role_to_dict(role) for role in roles]


def list_admin_users(db: Session, factory_id: str | None = None) -> list[dict[str, Any]]:
    query = db.query(AdminUser).options(joinedload(AdminUser.role), joinedload(AdminUser.factory))
    if factory_id:
        query = query.filter(AdminUser.factory_id == uuid.UUID(factory_id))
    return [public_user_dict(db, row) for row in query.order_by(AdminUser.created_at).all()]


def get_user_by_id(db: Session, user_id: str) -> AdminUser | None:
    return (
        db.query(AdminUser)
        .options(joinedload(AdminUser.role), joinedload(AdminUser.factory))
        .filter(AdminUser.id == uuid.UUID(user_id))
        .first()
    )


def get_user_by_email(db: Session, email: str) -> AdminUser | None:
    return (
        db.query(AdminUser)
        .options(joinedload(AdminUser.role), joinedload(AdminUser.factory))
        .filter(AdminUser.email == email)
        .first()
    )


def authenticate_user(db: Session, email: str, password: str) -> AdminUser | None:
    from app.core.security import verify_password

    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


def create_admin_user(
    db: Session,
    *,
    name: str,
    email: str,
    phone: str | None,
    role_code: str,
    factory_id: str | None,
    password: str = "123456",
) -> dict[str, Any]:
    role = db.query(Role).filter(Role.code == role_code).first()
    if not role:
        raise ValueError(f"Unknown role: {role_code}")
    row = AdminUser(
        factory_id=uuid.UUID(factory_id) if factory_id else None,
        role_id=role.id,
        name=name,
        email=email,
        phone=phone,
        password_hash=hash_password(password),
        status="active",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    row = get_user_by_id(db, str(row.id))
    assert row is not None
    return public_user_dict(db, row)


def update_admin_user(db: Session, user_id: str, payload: dict[str, Any]) -> dict[str, Any] | None:
    row = get_user_by_id(db, user_id)
    if not row:
        return None
    if "name" in payload:
        row.name = payload["name"]
    if "phone" in payload:
        row.phone = payload["phone"]
    if "status" in payload:
        row.status = payload["status"]
    if "role_code" in payload:
        role = db.query(Role).filter(Role.code == payload["role_code"]).first()
        if role:
            row.role_id = role.id
    db.commit()
    row = get_user_by_id(db, user_id)
    assert row is not None
    return public_user_dict(db, row)


def update_last_login(db: Session, user_id: str, last_login_at) -> None:
    row = db.get(AdminUser, uuid.UUID(user_id))
    if row:
        row.last_login_at = last_login_at
        db.commit()


def ensure_permissions(db: Session, permission_defs: list[dict[str, str]]) -> dict[str, Permission]:
    existing = {item.code: item for item in db.query(Permission).all()}
    for item in permission_defs:
        if item["code"] not in existing:
            perm = Permission(code=item["code"], name=item["name"], module=item["module"])
            db.add(perm)
            existing[item["code"]] = perm
    db.commit()
    return existing
