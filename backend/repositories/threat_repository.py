from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from typing import Optional
from ..models.threat import Threat, Prediction, MLModel
from .base import BaseRepository


class ThreatRepository(BaseRepository[Threat]):
    def __init__(self, session: AsyncSession):
        super().__init__(Threat, session)

    async def get_threat_stats(self, since: Optional[datetime] = None) -> dict:
        base_filter = [Threat.is_deleted == False]
        if since:
            base_filter.append(Threat.created_at >= since)

        total_query = select(func.count(Threat.id)).where(*base_filter)
        total_result = await self.session.execute(total_query)
        total = total_result.scalar() or 0

        by_type_query = select(Threat.threat_type, func.count(Threat.id)).where(
            *base_filter
        ).group_by(Threat.threat_type)
        by_type_result = await self.session.execute(by_type_query)
        by_type = {row[0]: row[1] for row in by_type_result}

        by_severity_query = select(Threat.severity, func.count(Threat.id)).where(
            *base_filter
        ).group_by(Threat.severity)
        by_severity_result = await self.session.execute(by_severity_query)
        by_severity = {row[0]: row[1] for row in by_severity_result}

        return {
            "total_threats": total,
            "by_type": by_type,
            "by_severity": by_severity,
        }


class PredictionRepository(BaseRepository[Prediction]):
    def __init__(self, session: AsyncSession):
        super().__init__(Prediction, session)

    async def get_prediction_stats(self, since: Optional[datetime] = None) -> dict:
        base_filter = [Prediction.is_deleted == False]
        if since:
            base_filter.append(Prediction.created_at >= since)

        total_query = select(func.count(Prediction.id)).where(*base_filter)
        total_result = await self.session.execute(total_query)
        total = total_result.scalar() or 0

        threat_query = select(func.count(Prediction.id)).where(*base_filter, Prediction.is_threat == True)
        threat_result = await self.session.execute(threat_query)
        threats = threat_result.scalar() or 0

        safe_query = select(func.count(Prediction.id)).where(*base_filter, Prediction.is_threat == False)
        safe_result = await self.session.execute(safe_query)
        safe = safe_result.scalar() or 0

        return {
            "total_predictions": total,
            "threats": threats,
            "safe": safe,
            "threat_percentage": (threats / total * 100) if total > 0 else 0,
        }


class MLModelRepository(BaseRepository[MLModel]):
    def __init__(self, session: AsyncSession):
        super().__init__(MLModel, session)

    async def get_active_model(self) -> MLModel:
        query = select(MLModel).where(
            MLModel.is_deleted == False,
            MLModel.is_active == True,
            MLModel.is_trained == True,
        ).limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def deactivate_all(self) -> None:
        query = select(MLModel).where(MLModel.is_active == True)
        result = await self.session.execute(query)
        models = result.scalars().all()
        for model in models:
            model.is_active = False
        await self.session.flush()
