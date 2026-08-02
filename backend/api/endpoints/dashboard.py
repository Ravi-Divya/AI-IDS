from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone
from ...database.session import get_session
from ...models.packet import Packet, Flow
from ...models.threat import Threat, Prediction, MLModel
from ...models.alert import Alert
from ...middleware.auth_middleware import get_current_user

router = APIRouter()


@router.get("/stats")
async def dashboard_stats(
    hours: int = Query(24, ge=1, le=720),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)

    packet_total = await session.scalar(select(func.count(Packet.id)).where(Packet.is_deleted == False))
    packet_recent = await session.scalar(select(func.count(Packet.id)).where(Packet.is_deleted == False, Packet.timestamp >= since))

    flow_total = await session.scalar(select(func.count(Flow.id)).where(Flow.is_deleted == False))
    flow_active = await session.scalar(select(func.count(Flow.id)).where(Flow.is_deleted == False, Flow.is_active == True))

    threat_total = await session.scalar(select(func.count(Threat.id)).where(Threat.is_deleted == False))
    threat_recent = await session.scalar(select(func.count(Threat.id)).where(Threat.is_deleted == False, Threat.created_at >= since))

    alert_total = await session.scalar(select(func.count(Alert.id)).where(Alert.is_deleted == False))
    alert_unread = await session.scalar(select(func.count(Alert.id)).where(Alert.is_deleted == False, Alert.is_read == False))

    predict_total = await session.scalar(select(func.count(Prediction.id)).where(Prediction.is_deleted == False))
    predict_threat = await session.scalar(select(func.count(Prediction.id)).where(Prediction.is_deleted == False, Prediction.is_threat == True))

    threats_by_type = {}
    type_rows = await session.execute(
        select(Threat.threat_type, func.count(Threat.id)).where(Threat.is_deleted == False).group_by(Threat.threat_type)
    )
    for row in type_rows:
        threats_by_type[row[0]] = row[1]

    threats_by_severity = {}
    sev_rows = await session.execute(
        select(Threat.severity, func.count(Threat.id)).where(Threat.is_deleted == False).group_by(Threat.severity)
    )
    for row in sev_rows:
        threats_by_severity[row[0]] = row[1]

    model_acc = await session.scalar(
        select(MLModel.accuracy).where(MLModel.is_active == True, MLModel.is_trained == True).limit(1)
    )

    time_span = (datetime.now(timezone.utc) - since).total_seconds()
    pps = (packet_recent or 0) / time_span if time_span > 0 else 0

    return {
        "total_packets": packet_total or 0,
        "recent_packets": packet_recent or 0,
        "total_flows": flow_total or 0,
        "active_flows": flow_active or 0,
        "total_threats": threat_total or 0,
        "recent_threats": threat_recent or 0,
        "total_alerts": alert_total or 0,
        "unread_alerts": alert_unread or 0,
        "total_predictions": predict_total or 0,
        "threat_predictions": predict_threat or 0,
        "threats_by_type": threats_by_type,
        "threats_by_severity": threats_by_severity,
        "model_accuracy": model_acc,
        "packets_per_second": round(pps, 2),
        "prediction_threat_percentage": round((predict_threat or 0) / (predict_total or 1) * 100, 2),
        "cpu_usage": 0.0,
        "memory_usage": 0.0,
    }


@router.get("/recent-threats")
async def recent_threats(
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    from ...schemas.packet import ThreatResponse
    from ...repositories.threat_repository import ThreatRepository
    repo = ThreatRepository(session)
    items_list, _ = await repo.get_all(limit=limit, order_by="created_at", order_desc=True)
    return [ThreatResponse.model_validate(t) for t in items_list]


@router.get("/traffic-timeline")
async def traffic_timeline(
    hours: int = Query(24, ge=1, le=168),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    from ...repositories.packet_repository import PacketRepository
    repo = PacketRepository(session)

    packets, _ = await repo.get_all(
        limit=1000,
        order_by="timestamp",
        order_desc=False,
    )

    timeline = {}
    for p in packets:
        hour_key = p.timestamp.strftime("%Y-%m-%d %H:00")
        if hour_key not in timeline:
            timeline[hour_key] = {"packets": 0, "threats": 0}
        timeline[hour_key]["packets"] += 1

    threat_rows = await session.execute(
        select(Threat.created_at).where(Threat.is_deleted == False, Threat.created_at >= since)
    )
    for row in threat_rows:
        hour_key = row[0].strftime("%Y-%m-%d %H:00")
        if hour_key in timeline:
            timeline[hour_key]["threats"] = timeline[hour_key].get("threats", 0) + 1

    result = [{"time": k, **v} for k, v in sorted(timeline.items())]
    return result
