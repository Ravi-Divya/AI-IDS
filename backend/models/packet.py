from datetime import datetime
from sqlalchemy import Column, String, Integer, BigInteger, Float, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.base_model import BaseModel


class Packet(BaseModel):
    __tablename__ = "packets"

    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    src_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    dst_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    protocol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    src_port: Mapped[int] = mapped_column(Integer, nullable=True)
    dst_port: Mapped[int] = mapped_column(Integer, nullable=True)
    packet_size: Mapped[int] = mapped_column(Integer, nullable=False)
    payload_size: Mapped[int] = mapped_column(Integer, nullable=True)
    ttl: Mapped[int] = mapped_column(Integer, nullable=True)
    window_size: Mapped[int] = mapped_column(Integer, nullable=True)
    tcp_flags: Mapped[str] = mapped_column(String(50), nullable=True)
    checksum: Mapped[str] = mapped_column(String(50), nullable=True)
    ip_version: Mapped[int] = mapped_column(Integer, nullable=True)
    tos: Mapped[int] = mapped_column(Integer, nullable=True)
    identification: Mapped[int] = mapped_column(Integer, nullable=True)
    fragment_offset: Mapped[int] = mapped_column(Integer, nullable=True)
    packet_entropy: Mapped[float] = mapped_column(Float, nullable=True)
    raw_headers: Mapped[dict] = mapped_column(JSONB, nullable=True)
    capture_interface: Mapped[str] = mapped_column(String(100), nullable=True)
    is_ipv6: Mapped[bool] = mapped_column(default=False)
    vlan_id: Mapped[int] = mapped_column(Integer, nullable=True)
    mpls_label: Mapped[str] = mapped_column(String(50), nullable=True)
    dns_query: Mapped[str] = mapped_column(String(500), nullable=True)
    http_method: Mapped[str] = mapped_column(String(10), nullable=True)
    http_uri: Mapped[str] = mapped_column(String(2000), nullable=True)
    http_host: Mapped[str] = mapped_column(String(500), nullable=True)
    http_user_agent: Mapped[str] = mapped_column(String(1000), nullable=True)
    ssh_version: Mapped[str] = mapped_column(String(100), nullable=True)
    ftp_command: Mapped[str] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        Index("idx_packets_protocol_timestamp", "protocol", "timestamp"),
        Index("idx_packets_src_dst", "src_ip", "dst_ip"),
    )


class Flow(BaseModel):
    __tablename__ = "flows"

    flow_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    src_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    dst_ip: Mapped[str] = mapped_column(String(45), nullable=False, index=True)
    src_port: Mapped[int] = mapped_column(Integer, nullable=False)
    dst_port: Mapped[int] = mapped_column(Integer, nullable=False)
    protocol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    duration: Mapped[float] = mapped_column(Float, nullable=True)

    packets_forward: Mapped[int] = mapped_column(BigInteger, default=0)
    packets_backward: Mapped[int] = mapped_column(BigInteger, default=0)
    bytes_forward: Mapped[int] = mapped_column(BigInteger, default=0)
    bytes_backward: Mapped[int] = mapped_column(BigInteger, default=0)

    avg_packet_size: Mapped[float] = mapped_column(Float, nullable=True)
    avg_forward_packet_size: Mapped[float] = mapped_column(Float, nullable=True)
    avg_backward_packet_size: Mapped[float] = mapped_column(Float, nullable=True)

    packets_per_second: Mapped[float] = mapped_column(Float, nullable=True)
    flow_bytes_per_second: Mapped[float] = mapped_column(Float, nullable=True)

    min_packet_size: Mapped[int] = mapped_column(Integer, nullable=True)
    max_packet_size: Mapped[int] = mapped_column(Integer, nullable=True)
    std_packet_size: Mapped[float] = mapped_column(Float, nullable=True)
    packet_size_variance: Mapped[float] = mapped_column(Float, nullable=True)

    min_ttl: Mapped[int] = mapped_column(Integer, nullable=True)
    max_ttl: Mapped[int] = mapped_column(Integer, nullable=True)
    avg_ttl: Mapped[float] = mapped_column(Float, nullable=True)

    tcp_syn_count: Mapped[int] = mapped_column(Integer, default=0)
    tcp_ack_count: Mapped[int] = mapped_column(Integer, default=0)
    tcp_fin_count: Mapped[int] = mapped_column(Integer, default=0)
    tcp_rst_count: Mapped[int] = mapped_column(Integer, default=0)
    tcp_psh_count: Mapped[int] = mapped_column(Integer, default=0)
    tcp_urg_count: Mapped[int] = mapped_column(Integer, default=0)
    tcp_flags_mask: Mapped[int] = mapped_column(Integer, default=0)

    window_size_avg: Mapped[float] = mapped_column(Float, nullable=True)
    window_size_min: Mapped[int] = mapped_column(Integer, nullable=True)
    window_size_max: Mapped[int] = mapped_column(Integer, nullable=True)

    idle_time: Mapped[float] = mapped_column(Float, nullable=True)
    active_time: Mapped[float] = mapped_column(Float, nullable=True)
    mean_flow_idle: Mapped[float] = mapped_column(Float, nullable=True)
    max_flow_idle: Mapped[float] = mapped_column(Float, nullable=True)

    dns_query_count: Mapped[int] = mapped_column(Integer, default=0)
    http_request_count: Mapped[int] = mapped_column(Integer, default=0)
    ssh_attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    ftp_command_count: Mapped[int] = mapped_column(Integer, default=0)

    entropy_avg: Mapped[float] = mapped_column(Float, nullable=True)
    burst_rate: Mapped[float] = mapped_column(Float, nullable=True)
    retransmission_count: Mapped[int] = mapped_column(Integer, default=0)
    urgent_data_count: Mapped[int] = mapped_column(Integer, default=0)

    unique_dst_ports: Mapped[int] = mapped_column(Integer, default=0)
    connection_frequency: Mapped[float] = mapped_column(Float, nullable=True)
    round_trip_time_avg: Mapped[float] = mapped_column(Float, nullable=True)

    is_complete: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    predictions = relationship("Prediction", back_populates="flow", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_flows_active", "is_active"),
        Index("idx_flows_src_dst_proto", "src_ip", "dst_ip", "protocol"),
    )
