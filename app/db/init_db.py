import asyncio
from app.db.base import Base
from app.models.report import Report
from app.models.history import History
from app.db.database import my_engine

async def init_db():
    try:
        async with my_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db())