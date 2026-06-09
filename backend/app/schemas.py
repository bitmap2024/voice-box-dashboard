from typing import Any

from pydantic import BaseModel


class LoginRequest(BaseModel):
    account: str
    password: str


class FactoryCreate(BaseModel):
    name: str
    industry: str = "AI 玩具"
    plan_type: str = "Professional"


class AdminUserCreate(BaseModel):
    name: str
    email: str
    phone: str | None = None
    role_code: str
    factory_id: str | None = None


class DeviceBindRequest(BaseModel):
    sn: str
    mac_address: str
    model: str = "VB-ESP32-S3"
    firmware_version: str = "1.0.0"
    batch_no: str = "B202606"
    character_id: str | None = None


class CharacterCreate(BaseModel):
    name: str
    scene_type: str
    age_range: str = "3-8 岁"
    tone_style: str = "温柔、活泼"
    description: str = ""


class PromptVersionCreate(BaseModel):
    version: str
    system_prompt: str
    change_note: str = ""
    structured_config: dict[str, Any] = {}
