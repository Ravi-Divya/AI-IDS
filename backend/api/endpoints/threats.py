from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta, timezone
from ...database.session import get_session
from ...schemas.packet import ThreatResponse, ThreatListResponse, PredictionResponse
from ...repositories.threat_repository import ThreatRepository, PredictionRepository, MLModelRepository
from ...middleware.auth_middleware import get_current_user

router = APIRouter()


@router.get("/", response_model=ThreatListResponse)
async def list_threats(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    threat_type: Optional[str] = None,
    severity: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    filters = {"is_deleted": False}
    if threat_type:
        filters["threat_type"] = threat_type
    if severity:
        filters["severity"] = severity

    repo = ThreatRepository(session)
    items, total = await repo.get_all(skip=(page - 1) * page_size, limit=page_size, filters=filters, order_by="created_at", order_desc=True)
    return {
        "items": [ThreatResponse.model_validate(t) for t in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/stats")
async def threat_stats(
    hours: int = Query(24, ge=1, le=720),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    repo = ThreatRepository(session)
    return await repo.get_threat_stats(since)


@router.get("/{threat_id}", response_model=ThreatResponse)
async def get_threat(
    threat_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    repo = ThreatRepository(session)
    threat = await repo.get(threat_id)
    if not threat:
        from ...middleware.error_handler import NotFoundException
        raise NotFoundException("Threat", threat_id)
    return ThreatResponse.model_validate(threat)


@router.get("/predictions/all")
async def list_predictions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    repo = PredictionRepository(session)
    items, total = await repo.get_all(skip=(page - 1) * page_size, limit=page_size, order_by="created_at", order_desc=True)
    return {
        "items": [PredictionResponse.model_validate(p) for p in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/predictions/stats")
async def prediction_stats(
    hours: int = Query(24, ge=1, le=720),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    repo = PredictionRepository(session)
    return await repo.get_prediction_stats(since)
