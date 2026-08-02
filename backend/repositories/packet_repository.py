from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from typing import Optional
from ..models.packet import Packet, Flow
from .base import BaseRepository


class PacketRepository(BaseRepository[Packet]):
    def __init__(self, session: AsyncSession):
        super().__init__(Packet, session)

    async def get_packets_in_range(
        self, start_time: datetime, end_time: datetime, skip: int = 0, limit: int = 1000
    ) -> list[Packet]:
        query = select(Packet).where(
            Packet.is_deleted == False,
            Packet.timestamp >= start_time,
            Packet.timestamp <= end_time,
        ).order_by(Packet.timestamp.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_protocol(self, since: Optional[datetime] = None) -> dict:
        query = select(Packet.protocol, func.count(Packet.id)).where(Packet.is_deleted == False)
        if since:
            query = query.where(Packet.timestamp >= since)
        query = query.group_by(Packet.protocol)
        result = await self.session.execute(query)
        return {row[0]: row[1] for row in result}

    async def get_traffic_stats(self, since: Optional[datetime] = None) -> dict:
        base_filter = [Packet.is_deleted == False]
        if since:
            base_filter.append(Packet.timestamp >= since)

        total = await self.count()
        avg_size_query = select(func.avg(Packet.packet_size)).where(*base_filter)
        avg_size_result = await self.session.execute(avg_size_query)
        avg_size = avg_size_result.scalar() or 0

        total_bytes_query = select(func.sum(Packet.packet_size)).where(*base_filter)
        total_bytes_result = await self.session.execute(total_bytes_query)
        total_bytes = total_bytes_result.scalar() or 0

        protocol_counts = await self.count_by_protocol(since)

        return {
            "total_packets": total,
            "average_packet_size": float(avg_size),
            "total_bytes": total_bytes,
            "protocols": protocol_counts,
        }


class FlowRepository(BaseRepository[Flow]):
    def __init__(self, session: AsyncSession):
        super().__init__(Flow, session)

    async def get_active_flows(self) -> list[Flow]:
        query = select(Flow).where(
            Flow.is_deleted == False,
            Flow.is_active == True,
        ).order_by(Flow.start_time.desc())
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_flow_key(self, flow_key: str) -> Flow:
        query = select(Flow).where(
            Flow.flow_key == flow_key,
            Flow.is_deleted == False,
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_flow_stats(self, since: Optional[datetime] = None) -> dict:
        base_filter = [Flow.is_deleted == False]
        if since:
            base_filter.append(Flow.start_time >= since)

        total_query = select(func.count(Flow.id)).where(*base_filter)
        total_result = await self.session.execute(total_query)
        total_flows = total_result.scalar()

        avg_duration_query = select(func.avg(Flow.duration)).where(*base_filter)
        avg_duration_result = await self.session.execute(avg_duration_query)
        avg_duration = avg_duration_result.scalar() or 0

        threat_query = select(func.count(Flow.id)).where(
            *base_filter, Flow.packets_forward > 100
        )
        threat_result = await self.session.execute(threat_query)

        return {
            "total_flows": total_flows or 0,
            "average_duration": float(avg_duration or 0),
            "active_flows": len(await self.get_active_flows()),
        }
