from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from database.engine import async_session
from database.models import Category, Product
from sqlalchemy import select

async def get_categories_keyboard():
    """Kategoriyalarni inline tugma qilib chiqarish (faqat mahsuloti borlari)"""
    builder = InlineKeyboardBuilder()
    
    async with async_session() as session:
        # Faqat o'zida stock > 0 bo'lgan mahsulotlari bor kategoriyalarni olamiz
        stmt = select(Category).join(Product).where(Product.stock > 0).distinct()
        result = await session.execute(stmt)
        categories = result.scalars().all()
        
        if not categories:
            return None
            
        for cat in categories:
            builder.button(text=cat.name, callback_data=f"cat_{cat.id}")
            
    # Tugmalarni 2 tadan yonma-yon qilib joylashtiramiz
    builder.adjust(2)
    return builder.as_markup()

async def get_admin_categories_keyboard():
    """Admin uchun Kategoriyalarni inline tugma qilib chiqarish"""
    builder = InlineKeyboardBuilder()
    
    async with async_session() as session:
        result = await session.execute(select(Category))
        categories = result.scalars().all()
        
        for cat in categories:
            builder.button(text=cat.name, callback_data=f"admincat_{cat.id}")
            
    builder.adjust(2)
    return builder.as_markup()

async def get_warehouse_keyboard():
    """Ombor uchun mahsulotlar ro'yxatini chiqarish"""
    builder = InlineKeyboardBuilder()
    
    async with async_session() as session:
        result = await session.execute(select(Product))
        products = result.scalars().all()
        
        for p in products:
            builder.button(text=f"{p.name} ({p.stock} ta | {p.price:,.0f} so'm)", callback_data=f"manageprod_{p.id}")
            
    builder.adjust(1) # Har bir mahsulot bitta qatorda chiqadi
    builder.row(InlineKeyboardButton(text="➕ Yangi mahsulot qo'shish", callback_data="admin_add_product"))
    return builder.as_markup()

def get_manage_product_keyboard(product_id: int):
    """Mahsulot soni yoki narxini o'zgartirish tugmalari"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📦 Sonini o'zgartirish", callback_data=f"editstock_{product_id}")
    builder.button(text="💰 Narxini o'zgartirish", callback_data=f"editprice_{product_id}")
    builder.adjust(1)
    return builder.as_markup()

def get_product_keyboard(category_id: int, current_index: int, total_count: int, product_id: int):
    """Mijozga bitta mahsulotni ko'rsatish va varaqlash uchun klaviatura"""
    builder = InlineKeyboardBuilder()
    
    # Varaqlash (Pagination) tugmalari (faqat 1 tadan ko'p bo'lsa)
    if total_count > 1:
        prev_idx = current_index - 1 if current_index > 0 else total_count - 1
        next_idx = current_index + 1 if current_index < total_count - 1 else 0
        builder.button(text="⬅️", callback_data=f"prod_{category_id}_{prev_idx}")
        builder.button(text=f"{current_index + 1}/{total_count}", callback_data="ignore")
        builder.button(text="➡️", callback_data=f"prod_{category_id}_{next_idx}")
        
    # Savatga qo'shish
    builder.button(text="🛒 Savatga qo'shish", callback_data=f"addcart_{product_id}")
    builder.button(text="🔙 Kategoriyalarga qaytish", callback_data="back_to_cat")
    
    # Qatorlarni moslash (varaqlash 3 ta, qolganlar 1 tadan)
    builder.adjust(3 if total_count > 1 else 1, 1, 1)
    return builder.as_markup()

def get_order_admin_keyboard(order_id: int):
    """Admin uchun buyurtmani boshqarish klaviaturasi"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Topshirildi", callback_data=f"order_complete_{order_id}")
    builder.button(text="❌ Bekor qilish", callback_data=f"order_cancel_{order_id}")
    builder.adjust(2)
    return builder.as_markup()
