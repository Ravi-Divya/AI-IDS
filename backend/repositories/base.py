from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, delete, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from ..database.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get(self, id: UUID) -> Optional[ModelType]:
        query = select(self.model).where(
            self.model.id == id,
            self.model.is_deleted == False,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = True,
    ) -> tuple[List[ModelType], int]:
        query = select(self.model).where(self.model.is_deleted == False)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        if order_by and hasattr(self.model, order_by):
            order_col = getattr(self.model, order_by)
            query = query.order_by(order_col.desc() if order_desc else order_col.asc())

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def update(self, id: UUID, **kwargs) -> Optional[ModelType]:
        instance = await self.get(id)
        if not instance:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        instance.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return instance

    async def soft_delete(self, id: UUID) -> bool:
        instance = await self.get(id)
        if not instance:
            return False
        instance.soft_delete()
        await self.session.flush()
        return True

    async def hard_delete(self, id: UUID) -> bool:
        query = delete(self.model).where(
            self.model.id == id,
            self.model.is_deleted == False,
        )
        result = await self.session.execute(query)
        return result.rowcount > 0

    async def exists(self, **filters) -> bool:
        query = select(self.model).where(self.model.is_deleted == False)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.first() is not None

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        query = select(func.count()).select_from(self.model).where(
            self.model.is_deleted == False,
        )
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalar()

    async def bulk_create(self, items: List[Dict[str, Any]]) -> List[ModelType]:
        instances = [self.model(**item) for item in items]
        self.session.add_all(instances)
        await self.session.flush()
        return instances

    async def get_or_create(self, defaults: Optional[Dict] = None, **kwargs) -> tuple[ModelType, bool]:
        instance = await self.get_by(**kwargs)
        if instance:
            return instance, False
        params = {**kwargs, **(defaults or {})}
        instance = await self.create(**params)
        return instance, True

    async def get_by(self, **kwargs) -> Optional[ModelType]:
        query = select(self.model).where(self.model.is_deleted == False)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
