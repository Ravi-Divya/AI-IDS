import structlog
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

import sqlalchemy as sa
from .config.settings import settings
from .core.logging import setup_logging, get_logger
from .middleware.error_handler import global_exception_handler, AppException
from .database.session import engine, Base
from .api.router import api_router
from .api.health import health_router

setup_logging()
logger = get_logger(__name__)


async def seed_default_roles(engine_instance):
    """Create default roles and promote first user to admin if no admin exists."""
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
    from sqlalchemy import select
    from .models.user import Role, User, user_roles

    session_factory = async_sessionmaker(engine_instance, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        try:
            # Create default roles if they don't exist
            for role_name, description, is_system in [
                ("admin", "Full system administrator", True),
                ("viewer", "Read-only access", True),
                ("analyst", "Security analyst with threat management", True),
            ]:
                existing = await session.execute(select(Role).where(Role.name == role_name))
                if not existing.scalar_one_or_none():
                    role = Role(name=role_name, description=description, is_system_role=is_system)
                    session.add(role)
                    logger.info("Created role", role=role_name)

            await session.commit()

            # Check if any user has admin role
            admin_role = await session.execute(select(Role).where(Role.name == "admin"))
            admin_role = admin_role.scalar_one_or_none()
            if admin_role:
                admin_check = await session.execute(
                    select(user_roles).where(user_roles.c.role_id == admin_role.id)
                )
                if not admin_check.first():
                    # No admin exists - promote the first user
                    first_user = await session.execute(
                        select(User).order_by(User.created_at.asc()).limit(1)
                    )
                    first_user = first_user.scalar_one_or_none()
                    if first_user:
                        first_user.roles.append(admin_role)
                        await session.commit()
                        logger.info("Promoted first user to admin", user=first_user.username)

        except Exception as e:
            logger.warning("Could not seed default roles", error=str(e))


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI-IDS application", version=settings.APP_VERSION, environment=settings.ENVIRONMENT)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            # Add company_name column if missing (existing database migration)
            await conn.execute(
                sa.text("ALTER TABLE users ADD COLUMN IF NOT EXISTS company_name VARCHAR(255)")
            )
        logger.info("Database tables created")
        await seed_default_roles(engine)
    except Exception as e:
        logger.warning("Could not connect to database on startup", error=str(e))
        logger.warning("App will start without database - ensure DATABASE_URL is configured")
    yield
    try:
        await engine.dispose()
    except Exception:
        pass
    logger.info("Application shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise-Grade AI-Driven Intrusion Detection System",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info("Request", method=request.method, path=request.url.path)
    response = await call_next(request)
    logger.info("Response", status=response.status_code)
    return response


app.add_exception_handler(Exception, global_exception_handler)


app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(api_router, prefix="/api/v1", tags=["API"])


if settings.VERCEL:
    logger.info("Vercel deployment - frontend served by Vercel static files")

    @app.get("/")
    async def root():
        return {
            "app": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
            "docs": "/api/docs",
        }
else:
    frontend_dist = (Path(__file__).parent / settings.FRONTEND_DIST_PATH).resolve()
    frontend_index = frontend_dist / "index.html"
    if frontend_dist.is_dir() and frontend_index.is_file():
        from fastapi.responses import FileResponse, HTMLResponse

        if (frontend_dist / "assets").is_dir():
            app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            if full_path.startswith("api/") or full_path.startswith("openapi"):
                from fastapi.exceptions import HTTPException
                raise HTTPException(status_code=404)
            if full_path.startswith("assets/"):
                from fastapi.exceptions import HTTPException
                raise HTTPException(status_code=404, detail="Asset not found")
            
            response = HTMLResponse(frontend_index.read_bytes())
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response

        logger.info("Frontend SPA mounted", path=str(frontend_dist))
    else:
        logger.warning("Frontend dist not found, API-only mode", path=str(frontend_dist))

        @app.get("/")
        async def root():
            return {
                "app": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "status": "running",
                "docs": "/api/docs",
            }


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Enterprise-Grade AI-Driven Intrusion Detection System",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {"url": "https://ai-ids.app/logo.png"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.getenv("PORT", str(settings.SERVER_PORT)))
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=port,
        reload=False,
        workers=settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )
