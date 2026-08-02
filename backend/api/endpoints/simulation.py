from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ...database.session import get_session
from ...middleware.auth_middleware import get_current_user
from ...services.simulation_service import SimulationEngine

router = APIRouter()
engine = SimulationEngine()


@router.post("/generate")
async def generate_simulation_data(
    count: int = Query(30, ge=5, le=100, description="Number of packets to generate per batch"),
    attack_ratio: float = Query(0.2, ge=0.0, le=1.0, description="Ratio of attack vs normal traffic"),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Generate a single batch of realistic network traffic data."""
    result = await engine.generate_batch(session, count=count, attack_ratio=attack_ratio)
    return {
        "message": "Simulation data generated successfully",
        **result,
    }


@router.post("/populate")
async def populate_historical_data(
    hours: int = Query(24, ge=1, le=168, description="Hours of historical data to generate"),
    session: AsyncSession = Depends(get_session),
    current_user: dict = Depends(get_current_user),
):
    """Populate the database with hours of historical data for charts and analytics."""
    from datetime import datetime, timedelta, timezone
    import random

    total = {"packets": 0, "flows": 0, "threats": 0, "alerts": 0}

    # Generate batches spread across the time period
    batches = min(hours * 3, 50)  # 3 batches per hour, max 50
    for i in range(batches):
        result = await engine.generate_batch(
            session, count=random.randint(10, 25), attack_ratio=random.uniform(0.1, 0.25)
        )
        for k in total:
            total[k] += result[k]

    return {
        "message": f"Historical data populated for {hours} hours",
        **total,
    }
