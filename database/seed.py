from sqlalchemy import select
from database.engine import async_session
from database.models import Category

async def seed_categories():
    """Boshlang'ich kategoriyalarni bazaga qo'shish"""
    categories_to_add = [
        "G'ildiraklar (Roliklar)", 
        "Petlalar", 
        "Relslar (Napravlyayushiy)", 
        "Mexanizmlar (Kargo)", 
        "Ugoloklar va mahkamlagichlar"
    ]
    
    async with async_session() as session:
        for cat_name in categories_to_add:
            # Agar baza ichida bu kategoriya bo'lmasa, qo'shamiz
            result = await session.execute(select(Category).where(Category.name == cat_name))
            if not result.scalar_one_or_none():
                session.add(Category(name=cat_name))
        await session.commit()
