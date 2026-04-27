from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.inline import get_categories_keyboard, get_product_keyboard
from database.engine import async_session
from database.models import Product
from sqlalchemy import select

router = Router()

@router.message(F.text == "🛍 Mahsulotlar")
async def show_categories(message: Message):
    """Mahsulotlar tugmasi bosilganda kategoriyalarni chiqarish"""
    keyboard = await get_categories_keyboard()
    if keyboard is None:
        await message.answer("🛒 Hozircha do'konimizda sotuvda mahsulotlar qolmadi (barchasi sotilib ketdi).")
    else:
        await message.answer("🛒 Quyidagi toifalardan birini tanlang:", reply_markup=keyboard)

@router.callback_query(F.data.startswith("cat_"))
async def show_products_by_category(callback: CallbackQuery):
    """Kategoriya tanlanganda ichidagi mahsulotlarni ko'rsatish (0-indeksdan boshlab)"""
    category_id = int(callback.data.split("_")[1])
    await show_product_by_index(callback, category_id, 0)

@router.callback_query(F.data.startswith("prod_"))
async def paginate_products(callback: CallbackQuery):
    """Mahsulotlarni o'ngga yoki chapga varaqlash"""
    parts = callback.data.split("_")
    category_id = int(parts[1])
    index = int(parts[2])
    await show_product_by_index(callback, category_id, index)

async def show_product_by_index(callback: CallbackQuery, category_id: int, index: int):
    async with async_session() as session:
        # MUHIM: Faqat omborda qoldig'i bor (stock > 0) bo'lgan mahsulotlarni olamiz
        result = await session.execute(
            select(Product).where(Product.category_id == category_id, Product.stock > 0).order_by(Product.id)
        )
        products = result.scalars().all()
        
    if not products:
        # Agar bu toifada stock > 0 mahsulot qolmagan bo'lsa
        try:
            await callback.message.edit_text(
                "📦 Ushbu toifada hozircha sotuvda (omborda) mahsulot yo'q.\n\nBoshqa toifani tanlab ko'ring.",
                reply_markup=await get_categories_keyboard()
            )
        except Exception:
            await callback.message.delete()
            await callback.message.answer(
                "📦 Ushbu toifada hozircha sotuvda (omborda) mahsulot yo'q.\n\nBoshqa toifani tanlab ko'ring.",
                reply_markup=await get_categories_keyboard()
            )
        await callback.answer()
        return
        
    if index >= len(products):
        index = 0
        
    product = products[index]
    total_count = len(products)
    
    text = (
        f"🏷 **{product.name}**\n\n"
        f"{product.description}\n\n"
        f"💰 Narxi: **{product.price:,.0f} so'm**\n"
        f"📦 Omborda: {product.stock} ta qoldi"
    )
    
    keyboard = get_product_keyboard(category_id, index, total_count, product.id)
    
    # Rasm yuborish uchun eski xabarni o'chirib, yangisini yuboramiz
    await callback.message.delete()
    
    if product.image_id:
        await callback.message.answer_photo(
            photo=product.image_id,
            caption=text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    else:
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
        
    await callback.answer()

@router.callback_query(F.data == "back_to_cat")
async def back_to_categories(callback: CallbackQuery):
    """Kategoriyalarga qaytish tugmasi"""
    keyboard = await get_categories_keyboard()
    await callback.message.delete()
    await callback.message.answer("🛒 Quyidagi toifalardan birini tanlang:", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    """1/5 kabi bet raqami yozilgan tugma bosilganda hech narsa qilmaslik"""
    await callback.answer()
