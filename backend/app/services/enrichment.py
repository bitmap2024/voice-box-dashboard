from sqlalchemy.orm import Session

from app.repositories.characters import get_character_name
from app.repositories.devices import get_device_sn


def device_name(db: Session, device_id: str) -> str:
    return get_device_sn(db, device_id)


def character_name(db: Session, character_id: str | None) -> str:
    if not character_id:
        return "-"
    return get_character_name(db, character_id)
