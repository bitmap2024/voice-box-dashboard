import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import DeviceStatus, SeverityLevel


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    factory_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("factories.id", ondelete="CASCADE"), nullable=False)
    sn: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    mac_address: Mapped[str] = mapped_column(String(80), nullable=False)
    model: Mapped[str] = mapped_column(String(80), nullable=False)
    firmware_version: Mapped[str] = mapped_column(String(40), nullable=False)
    batch_no: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[DeviceStatus] = mapped_column(default=DeviceStatus.offline)
    current_character_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_characters.id"))
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DeviceBinding(Base):
    __tablename__ = "device_bindings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    factory_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("factories.id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    sn: Mapped[str] = mapped_column(String(80), nullable=False)
    bind_status: Mapped[str] = mapped_column(String(40), nullable=False, default="bound")
    bound_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id"))
    bound_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    unbound_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DeviceTelemetry(Base):
    __tablename__ = "device_telemetry"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    factory_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("factories.id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    sn: Mapped[str] = mapped_column(String(80), nullable=False)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    online: Mapped[bool] = mapped_column(Boolean, nullable=False)
    wifi_rssi: Mapped[int | None] = mapped_column(Integer)
    websocket_connected: Mapped[bool | None] = mapped_column(Boolean)
    rtt_ms: Mapped[int | None] = mapped_column(Integer)
    reconnect_count: Mapped[int] = mapped_column(Integer, default=0)
    upload_fail_count: Mapped[int] = mapped_column(Integer, default=0)
    playback_fail_count: Mapped[int] = mapped_column(Integer, default=0)
    firmware_version: Mapped[str | None] = mapped_column(String(40))
    free_memory: Mapped[int | None] = mapped_column(Integer)
    cpu_usage: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    reboot_reason: Mapped[str | None] = mapped_column(String(120))
    audio_state: Mapped[str | None] = mapped_column(String(40))


class DeviceEvent(Base):
    __tablename__ = "device_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    factory_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("factories.id", ondelete="CASCADE"), nullable=False)
    device_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("devices.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[SeverityLevel] = mapped_column(default=SeverityLevel.low)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
