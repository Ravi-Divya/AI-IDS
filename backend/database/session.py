from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from ..config.settings import settings

if settings.is_serverless:
    engine = create_async_engine(
        settings.get_database_url(),
        echo=settings.DEBUG,
        pool_size=2,
        max_overflow=2,
        pool_pre_ping=True,
        pool_recycle=60,
        pool_use_lifo=True,
    )
else:
    engine = create_async_engine(
        settings.get_database_url(),
        echo=settings.DEBUG,
        pool_size=20,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
