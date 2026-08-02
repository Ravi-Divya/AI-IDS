from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from ...database.session import get_session
from ...schemas.packet import AlertResponse, AlertListResponse
from ...models.alert import Alert
from ...repositories.base import BaseRepository
from ...middleware.auth_middleware import get_current_user

router = APIRouter()


@router.get("/", response_model=AlertListResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    unread_only: bool = False,
    severity: str = None,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    repo = BaseRepository(Alert, session)
    filters = {"is_deleted": False}
    if unread_only:
        filters["is_read"] = False
    if severity:
        filters["severity"] = severity

    items, total = await repo.get_all(skip=(page - 1) * page_size, limit=page_size, filters=filters, order_by="created_at", order_desc=True)
    return {
        "items": [AlertResponse.model_validate(a) for a in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    repo = BaseRepository(Alert, session)
    alert = await repo.get(alert_id)
    if not alert:
        from ...middleware.error_handler import NotFoundException
        raise NotFoundException("Alert", alert_id)
    return AlertResponse.model_validate(alert)


@router.post("/{alert_id}/read")
async def mark_alert_read(
    alert_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    repo = BaseRepository(Alert, session)
    alert = await repo.update(alert_id, is_read=True)
    if not alert:
        from ...middleware.error_handler import NotFoundException
        raise NotFoundException("Alert", alert_id)
    return {"message": "Alert marked as read"}


@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    repo = BaseRepository(Alert, session)
    alert = await repo.update(
        alert_id,
        is_acknowledged=True,
        acknowledged_by=current_user.get("sub", ""),
        acknowledged_at=datetime.now(timezone.utc),
    )
    if not alert:
        from ...middleware.error_handler import NotFoundException
        raise NotFoundException("Alert", alert_id)
    return {"message": "Alert acknowledged"}


@router.get("/channels/status")
async def get_channel_status(current_user: dict = Depends(get_current_user)):
    from ...alerts.alert_engine import alert_engine
    return alert_engine.get_channel_status()
