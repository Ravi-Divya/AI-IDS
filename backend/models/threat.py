from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.base_model import BaseModel


class Threat(BaseModel):
    __tablename__ = "threats"

    threat_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    threat_level: Mapped[int] = mapped_column(Integer, default=0)
    src_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    dst_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    src_port: Mapped[int] = mapped_column(Integer, nullable=True)
    dst_port: Mapped[int] = mapped_column(Integer, nullable=True)
    protocol: Mapped[str] = mapped_column(String(20), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str] = mapped_column(Text, nullable=True)
    feature_importance: Mapped[dict] = mapped_column(JSONB, nullable=True)
    raw_features: Mapped[dict] = mapped_column(JSONB, nullable=True)
    is_mitigated: Mapped[bool] = mapped_column(Boolean, default=False)
    mitigated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    mitigated_by: Mapped[str] = mapped_column(String(255), nullable=True)
    flow_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("flows.id"), nullable=True)
    prediction_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("predictions.id"), nullable=True)

    prediction = relationship("Prediction", back_populates="threat", uselist=False)
    alerts = relationship("Alert", back_populates="threat", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_threats_type_severity", "threat_type", "severity"),
        Index("idx_threats_timestamp", "created_at"),
    )


class Prediction(BaseModel):
    __tablename__ = "predictions"

    flow_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("flows.id"), nullable=False, index=True)
    model_id: Mapped[str] = mapped_column(UUID(as_uuid=True), ForeignKey("ml_models.id"), nullable=True)
    predicted_class: Mapped[str] = mapped_column(String(100), nullable=False)
    predicted_label: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_scores: Mapped[dict] = mapped_column(JSONB, nullable=True)
    features_used: Mapped[list] = mapped_column(JSONB, nullable=True)
    feature_values: Mapped[dict] = mapped_column(JSONB, nullable=True)
    shap_values: Mapped[dict] = mapped_column(JSONB, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    prediction_time_ms: Mapped[float] = mapped_column(Float, nullable=True)
    is_threat: Mapped[bool] = mapped_column(Boolean, default=False)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)

    flow = relationship("Flow", back_populates="predictions")
    model = relationship("MLModel", back_populates="predictions")
    threat = relationship("Threat", back_populates="prediction", uselist=False)

    __table_args__ = (
        Index("idx_predictions_is_threat", "is_threat"),
        Index("idx_predictions_confidence", "confidence"),
    )


class MLModel(BaseModel):
    __tablename__ = "ml_models"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    model_type: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    file_path: Mapped[str] = mapped_column(String(500), nullable=True)
    parameters: Mapped[dict] = mapped_column(JSONB, nullable=True)
    metrics: Mapped[dict] = mapped_column(JSONB, nullable=True)
    accuracy: Mapped[float] = mapped_column(Float, nullable=True)
    precision_macro: Mapped[float] = mapped_column(Float, nullable=True)
    recall_macro: Mapped[float] = mapped_column(Float, nullable=True)
    f1_macro: Mapped[float] = mapped_column(Float, nullable=True)
    roc_auc: Mapped[float] = mapped_column(Float, nullable=True)
    confusion_matrix: Mapped[dict] = mapped_column(JSONB, nullable=True)
    feature_importance: Mapped[dict] = mapped_column(JSONB, nullable=True)
    training_dataset: Mapped[str] = mapped_column(String(200), nullable=True)
    training_samples: Mapped[int] = mapped_column(Integer, nullable=True)
    training_duration_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_trained: Mapped[bool] = mapped_column(Boolean, default=False)
    scaler_path: Mapped[str] = mapped_column(String(500), nullable=True)
    encoder_path: Mapped[str] = mapped_column(String(500), nullable=True)
    feature_columns: Mapped[list] = mapped_column(JSONB, nullable=True)

    predictions = relationship("Prediction", back_populates="model", cascade="all, delete-orphan")
