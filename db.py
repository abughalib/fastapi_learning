from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
import os


engine = create_async_engine(
    os.environ.get("DATABASE_URL") or "",
    pool_size=20,
    max_overflow=0,
)


async def get_session():
    session = AsyncSession(engine)
    try:
        yield session
    finally:
        await session.close()
