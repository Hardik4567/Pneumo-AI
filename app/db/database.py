import os
from dotenv import load_dotenv
from app.core.config import settings
from app.core.logger import app_logger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

load_dotenv()

# =====================================================
# MySQL (Primary Database)
# =====================================================

MYSQL_DATABASE_URL = (
    f"mysql+asyncmy://{settings.MYSQL_DB_USER}:{settings.MYSQL_DB_PASSWORD}@"
    f"{settings.MYSQL_DB_HOST}:{settings.MYSQL_DB_PORT}/{settings.MYSQL_DB_NAME}"
)

my_engine = create_async_engine(
    MYSQL_DATABASE_URL,
    echo=False,
    future=True,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=settings.MYSQL_DB_POOL_RECYCLE,
    pool_pre_ping=True,
)

MyAsyncSessionLocal = sessionmaker(
    bind=my_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)


# =====================================================
# Session Dependency
# =====================================================

async def get_db():
    async with MyAsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
