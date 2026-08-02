from fastapi import APIRouter
from .endpoints import auth, users, packets, threats, alerts, ml, dashboard, logs, settings, simulation

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(packets.router, prefix="/packets", tags=["Packets"])
api_router.include_router(threats.router, prefix="/threats", tags=["Threats"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(ml.router, prefix="/ml", tags=["Machine Learning"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(logs.router, prefix="/logs", tags=["Logs"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["Simulation"])

