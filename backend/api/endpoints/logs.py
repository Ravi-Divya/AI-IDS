from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ...database.session import get_session
from ...models.audit import AuditLog
from ...repositories.base import BaseRepository
from ...middleware.auth_middleware import get_current_user

router = APIRouter()


@router.get("/")
async def list_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    action: Optional[str] = None,
    resource: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    repo = BaseRepository(AuditLog, session)
    filters = {"is_deleted": False}
    if action:
        filters["action"] = action
    if resource:
        filters["resource"] = resource

    items, total = await repo.get_all(skip=(page - 1) * page_size, limit=page_size, filters=filters, order_by="created_at", order_desc=True)
    return {
        "items": [
            {
                "id": str(log.id),
                "user_id": str(log.user_id) if log.user_id else None,
                "action": log.action,
                "resource": log.resource,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "status": log.status,
                "created_at": log.created_at.isoformat(),
            }
            for log in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
