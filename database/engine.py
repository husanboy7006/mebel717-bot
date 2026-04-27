from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from config.config import DB_URL

# PostgreSQL ma'lumotlar bazasiga asinxron ulanish uchun dvigatel yaratamiz
engine = create_async_engine(DB_URL, echo=True)

# Asinxron sessiya yaratuvchi
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

# Barcha modellar shundan meros oladi
Base = declarative_base()

async def init_db():
    """Barcha jadvallarni bazada yaratish"""
    async with engine.begin() as conn:
        # Barcha jadvallarni yaratamiz (agar oldin yaratilmagan bo'lsa)
        await conn.run_sync(Base.metadata.create_all)
