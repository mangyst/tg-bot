from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession)  # type:ignore


async def get_async_session():
    """Генератор сессий."""
    async with AsyncSessionLocal() as async_session:
        yield async_session
