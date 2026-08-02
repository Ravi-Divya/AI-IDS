from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta, timezone
from ...database.session import get_session
from ...schemas.packet import PacketResponse, PacketListResponse, FlowResponse, FlowListResponse
from ...repositories.packet_repository import PacketRepository, FlowRepository
from ...middleware.auth_middleware import get_current_user

router = APIRouter()


@router.get("/", response_model=PacketListResponse)
async def list_packets(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    src_ip: Optional[str] = None,
    dst_ip: Optional[str] = None,
    protocol: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    filters = {}
    if src_ip:
        filters["src_ip"] = src_ip
    if dst_ip:
        filters["dst_ip"] = dst_ip
    if protocol:
        filters["protocol"] = protocol

    repo = PacketRepository(session)
    items, total = await repo.get_all(skip=(page - 1) * page_size, limit=page_size, filters=filters, order_by="timestamp", order_desc=True)
    return {
        "items": [PacketResponse.model_validate(p) for p in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/stats")
async def packet_stats(
    hours: int = Query(1, ge=1, le=168),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    repo = PacketRepository(session)
    return await repo.get_traffic_stats(since)


@router.get("/flows", response_model=FlowListResponse)
async def list_flows(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    active_only: bool = False,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    repo = FlowRepository(session)
    filters = {"is_active": active_only} if active_only else None
    items, total = await repo.get_all(skip=(page - 1) * page_size, limit=page_size, filters=filters, order_by="start_time", order_desc=True)
    return {
        "items": [FlowResponse.model_validate(f) for f in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/flows/stats")
async def flow_stats(
    hours: int = Query(1, ge=1, le=168),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    repo = FlowRepository(session)
    return await repo.get_flow_stats(since)
