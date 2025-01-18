from .database_schemes import Base
from .database_engine import engine

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
