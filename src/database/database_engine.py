from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from typing import AsyncGenerator

from src.settings import settings

engine = create_async_engine(
    url=settings.FULL_DB_URL,
    echo=settings.DB_ECHO
)

session_factory = async_sessionmaker(autocommit=False, bind=engine)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session
