from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID as _UUID


def _uuid_to_str(v):
    if isinstance(v, _UUID):
        return str(v)
    return v


class PacketResponse(BaseModel):
    id: str
    timestamp: datetime
    src_ip: str
    dst_ip: str
    protocol: str
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    packet_size: int
    payload_size: Optional[int] = None
    ttl: Optional[int] = None
    window_size: Optional[int] = None
    tcp_flags: Optional[str] = None
    checksum: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return _uuid_to_str(v)


class PacketListResponse(BaseModel):
    items: List[PacketResponse]
    total: int
    page: int
    page_size: int


class FlowResponse(BaseModel):
    id: str
    flow_key: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    packets_forward: int
    packets_backward: int
    bytes_forward: int
    bytes_backward: int
    packets_per_second: Optional[float] = None
    flow_bytes_per_second: Optional[float] = None
    is_active: bool
    is_complete: bool

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return _uuid_to_str(v)


class FlowListResponse(BaseModel):
    items: List[FlowResponse]
    total: int
    page: int
    page_size: int


class TrafficStatsResponse(BaseModel):
    total_packets: int
    total_flows: int
    active_flows: int
    packets_per_second: float
    average_packet_size: float
    total_bytes: int
    protocol_distribution: dict


class ThreatResponse(BaseModel):
    id: str
    threat_type: str
    severity: str
    confidence: float
    src_ip: str
    dst_ip: str
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    protocol: Optional[str] = None
    description: Optional[str] = None
    explanation: Optional[str] = None
    recommendation: Optional[str] = None
    is_mitigated: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return _uuid_to_str(v)


class ThreatListResponse(BaseModel):
    items: List[ThreatResponse]
    total: int
    page: int
    page_size: int


class PredictionResponse(BaseModel):
    id: str
    flow_id: str
    predicted_class: str
    confidence: float
    explanation: Optional[str] = None
    is_threat: bool
    prediction_time_ms: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", "flow_id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return _uuid_to_str(v)


class AlertResponse(BaseModel):
    id: str
    threat_id: str
    alert_type: str
    title: str
    message: str
    severity: str
    confidence: float
    threat_type: str
    src_ip: str
    dst_ip: str
    explanation: Optional[str] = None
    recommendation: Optional[str] = None
    is_read: bool
    is_acknowledged: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", "threat_id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return _uuid_to_str(v)


class AlertListResponse(BaseModel):
    items: List[AlertResponse]
    total: int
    page: int
    page_size: int


class MLModelResponse(BaseModel):
    id: str
    name: str
    model_type: str
    version: str
    accuracy: Optional[float] = None
    precision_macro: Optional[float] = None
    recall_macro: Optional[float] = None
    f1_macro: Optional[float] = None
    roc_auc: Optional[float] = None
    is_active: bool
    is_trained: bool
    training_dataset: Optional[str] = None
    training_samples: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("id", mode="before")
    @classmethod
    def coerce_id(cls, v):
        return _uuid_to_str(v)


class DashboardStatsResponse(BaseModel):
    total_packets: int
    total_flows: int
    active_flows: int
    total_threats: int
    total_alerts: int
    total_predictions: int
    threats_by_type: dict
    threats_by_severity: dict
    predictions_threat_percentage: float
    model_accuracy: Optional[float] = None
    packets_per_second: float
    cpu_usage: float
    memory_usage: float
