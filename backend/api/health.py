from fastapi import APIRouter, Depends
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database.session import get_session
from ..models import User, Role
from ..core.logging import get_logger

health_router = APIRouter()
logger = get_logger(__name__)


@health_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "uptime": "running",
    }


@health_router.get("/health/ready")
async def readiness_check():
    return {"status": "ready", "timestamp": datetime.now(timezone.utc).isoformat()}


@health_router.get("/health/live")
async def liveness_check():
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}


@health_router.get("/health/promote")
async def promote_user(username: str = "admin", session: AsyncSession = Depends(get_session)):
    try:
        # 1. Ensure default roles exist
        roles_created = []
        for role_name, description, is_system in [
            ("admin", "Full system administrator", True),
            ("viewer", "Read-only access", True),
            ("analyst", "Security analyst with threat management", True),
        ]:
            existing_role = await session.execute(select(Role).where(Role.name == role_name))
            role = existing_role.scalar_one_or_none()
            if not role:
                role = Role(name=role_name, description=description, is_system_role=is_system)
                session.add(role)
                roles_created.append(role_name)
        
        await session.commit()

        # 2. Find the role and the user
        admin_role_query = await session.execute(select(Role).where(Role.name == "admin"))
        admin_role = admin_role_query.scalar_one_or_none()

        user_query = await session.execute(select(User).where(User.username == username))
        user = user_query.scalar_one_or_none()

        if not user:
            return {"status": "error", "message": f"User '{username}' not found"}

        if admin_role not in user.roles:
            user.roles.append(admin_role)
            await session.commit()
            return {
                "status": "success",
                "message": f"User '{username}' promoted to admin role",
                "roles_created": roles_created,
                "user_roles": [r.name for r in user.roles]
            }
        else:
            return {
                "status": "already_admin",
                "message": f"User '{username}' already has admin role",
                "user_roles": [r.name for r in user.roles]
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}
