from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.base_model import BaseModel


class Alert(BaseModel):
    __tablename__ = "alerts"

    threat_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("threats.id"), nullable=False, index=True)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    threat_type: Mapped[str] = mapped_column(String(100), nullable=False)
    src_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    dst_ip: Mapped[str] = mapped_column(String(45), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    is_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_by: Mapped[str] = mapped_column(String(255), nullable=True)
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_status: Mapped[dict] = mapped_column(JSONB, nullable=True)

    threat = relationship("Threat", back_populates="alerts")

    __table_args__ = (
        Index("idx_alerts_severity_read", "severity", "is_read"),
        Index("idx_alerts_created", "created_at"),
    )


class NotificationHistory(BaseModel):
    __tablename__ = "notification_history"

    user_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    alert_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=True)
    channel: Mapped[str] = mapped_column(String(50), nullable=False)
    recipient: Mapped[str] = mapped_column(String(500), nullable=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index("idx_notifications_status", "status"),
        Index("idx_notifications_user", "user_id"),
    )
