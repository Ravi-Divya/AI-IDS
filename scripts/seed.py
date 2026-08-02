"""Seed the database with initial data including admin user and default roles."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database.session import async_session_factory, engine, Base
from backend.security.auth import hash_password
from backend.models.user import User, Role, Permission, RolePermission
from backend.models.audit import Setting


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "admin"))
        existing = result.scalar_one_or_none()
        if not existing:
            roles_data = [
                {"name": "admin", "description": "Full system access", "is_system_role": True},
                {"name": "analyst", "description": "Can view and acknowledge alerts", "is_system_role": True},
                {"name": "viewer", "description": "Read-only access to dashboard", "is_system_role": True},
            ]

            roles = {}
            for r in roles_data:
                role = Role(**r)
                session.add(role)
                roles[r["name"]] = role

            permissions_data = [
                {"name": "users.read", "resource": "users", "action": "read", "description": "View users"},
                {"name": "users.write", "resource": "users", "action": "write", "description": "Create/update users"},
                {"name": "users.delete", "resource": "users", "action": "delete", "description": "Delete users"},
                {"name": "alerts.read", "resource": "alerts", "action": "read", "description": "View alerts"},
                {"name": "alerts.acknowledge", "resource": "alerts", "action": "acknowledge", "description": "Acknowledge alerts"},
                {"name": "ml.train", "resource": "ml", "action": "train", "description": "Train ML models"},
                {"name": "ml.predict", "resource": "ml", "action": "predict", "description": "Make predictions"},
                {"name": "settings.read", "resource": "settings", "action": "read", "description": "View settings"},
                {"name": "settings.write", "resource": "settings", "action": "write", "description": "Update settings"},
                {"name": "logs.read", "resource": "logs", "action": "read", "description": "View audit logs"},
            ]

            for p in permissions_data:
                permission = Permission(**p)
                session.add(permission)

            admin_user = User(
                email="admin@aids.local",
                username="admin",
                hashed_password=hash_password("Admin123!"),
                full_name="System Administrator",
                is_active=True,
                is_verified=True,
            )
            admin_user.roles = [roles["admin"]]
            session.add(admin_user)

            analyst_user = User(
                email="analyst@aids.local",
                username="analyst",
                hashed_password=hash_password("Analyst123!"),
                full_name="Security Analyst",
                is_active=True,
                is_verified=True,
            )
            analyst_user.roles = [roles["analyst"]]
            session.add(analyst_user)

            viewer_user = User(
                email="viewer@aids.local",
                username="viewer",
                hashed_password=hash_password("Viewer123!"),
                full_name="Dashboard Viewer",
                is_active=True,
                is_verified=True,
            )
            viewer_user.roles = [roles["viewer"]]
            session.add(viewer_user)

            default_settings = [
                {"key": "packet_capture_enabled", "value": True, "category": "capture", "description": "Enable packet capture"},
                {"key": "confidence_threshold", "value": 0.85, "category": "ml", "description": "ML confidence threshold"},
                {"key": "alert_notifications_enabled", "value": True, "category": "alerts", "description": "Enable alert notifications"},
                {"key": "flow_idle_timeout", "value": 60, "category": "capture", "description": "Flow idle timeout in seconds"},
            ]
            for s in default_settings:
                session.add(Setting(**s))

            await session.commit()
            print("Database seeded successfully!")
            print("Admin credentials: admin / Admin123!")
            print("Analyst credentials: analyst / Analyst123!")
            print("Viewer credentials: viewer / Viewer123!")
        else:
            print("Database already seeded, skipping.")


if __name__ == "__main__":
    asyncio.run(seed())
