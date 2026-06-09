import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.enums import SeverityLevel


class FactoryDailyMetric(Base):
    __tablename__ = "factory_daily_metrics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    factory_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("factories.id", ondelete="CASCADE"), nullable=False)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False)
    active_device_count: Mapped[int] = mapped_column(Integer, default=0)
    online_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    conversation_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_turns: Mapped[Decimal | None] = mapped_column(Numeric(8, 2))
    success_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    fallback_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    p50_first_response_ms: Mapped[int | None] = mapped_column(Integer)
    p90_first_response_ms: Mapped[int | None] = mapped_column(Integer)
    p95_first_response_ms: Mapped[int | None] = mapped_column(Integer)
    asr_fail_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    tts_fail_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    llm_fail_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 3))
    cloud_cost_estimate: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))


class IndustryDailyBenchmark(Base):
    __tablename__ = "industry_daily_benchmarks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    industry: Mapped[str] = mapped_column(String(80), nullable=False)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False)
    metric_name: Mapped[str] = mapped_column(String(80), nullable=False)
    avg_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    median_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    p75_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    p90_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    top25_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))
    sample_factory_count: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    factory_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("factories.id", ondelete="CASCADE"), nullable=False)
    recommendation_type: Mapped[str] = mapped_column(String(80), nullable=False)
    severity: Mapped[SeverityLevel] = mapped_column(default=SeverityLevel.medium)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    factory_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("factories.id", ondelete="CASCADE"))
    admin_user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("admin_users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(80))
    target_id: Mapped[str | None] = mapped_column(String(120))
    ip: Mapped[str | None] = mapped_column(String(80))
    user_agent: Mapped[str | None] = mapped_column(Text)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
