from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from ...database.session import get_session
from ...models.audit import Setting
from ...repositories.base import BaseRepository
from ...middleware.auth_middleware import get_current_user

router = APIRouter()


@router.get("/")
async def list_settings(
    category: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    repo = BaseRepository(Setting, session)
    filters = {"is_deleted": False}
    if category:
        filters["category"] = category

    items, total = await repo.get_all(limit=200, filters=filters)
    return {
        "items": [
            {
                "id": str(s.id),
                "key": s.key,
                "value": s.value,
                "description": s.description,
                "category": s.category,
                "is_encrypted": s.is_encrypted,
            }
            for s in items
        ],
        "total": total,
    }


@router.put("/{key}")
async def update_setting(
    key: str,
    value: dict,
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    repo = BaseRepository(Setting, session)
    setting = await repo.get_by(key=key)
    if setting:
        await repo.update(setting.id, value=value)
    else:
        await repo.create(key=key, value=value)
    return {"message": f"Setting {key} updated"}
