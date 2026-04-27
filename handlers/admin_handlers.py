from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, Filter
from aiogram.fsm.context import FSMContext

from config.config import ADMIN_IDS
from utils.states import AddProductState, EditStockState, AddCategoryState, EditPriceState, BroadcastState
from keyboards.reply import get_admin_menu_keyboard, get_main_menu_keyboard
from keyboards.inline import get_admin_categories_keyboard, get_warehouse_keyboard, get_manage_product_keyboard
from database.engine import async_session
from database.models import Product, Category, Order, OrderItem, OrderStatus, User
from sqlalchemy import select, func

router = Router()

class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in ADMIN_IDS

# /admin komandasi
@router.message(Command("admin"), IsAdmin())
async def cmd_admin(message: Message):
    await message.answer("👑 Admin panelga xush kelibsiz!", reply_markup=get_admin_menu_keyboard())

# Oddiy menyuga qaytish
@router.message(F.text == "⬅️ Mijoz menyusi", IsAdmin())
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Mijoz menyusiga qaytdingiz.", reply_markup=get_main_menu_keyboard())

# --- KATEGORIYA QO'SHISH FSM ---

@router.message(F.text == "📁 Kategoriya qo'shish", IsAdmin())
async def start_add_category(message: Message, state: FSMContext):
    await message.answer("Yangi kategoriya nomini yozing ✍️\n(Masalan: Eshik tutqichlari):")
    await state.set_state(AddCategoryState.name)

@router.message(AddCategoryState.name, F.text, IsAdmin())
async def process_category_name(message: Message, state: FSMContext):
    cat_name = message.text
    
    async with async_session() as session:
        result = await session.execute(select(Category).where(Category.name == cat_name))
        existing_cat = result.scalar_one_or_none()
        
        if existing_cat:
            await message.answer(f"❌ '{cat_name}' nomli kategoriya allaqachon mavjud!", reply_markup=get_admin_menu_keyboard())
        else:
            new_cat = Category(name=cat_name)
            session.add(new_cat)
            await session.commit()
            await message.answer(f"✅ '{cat_name}' muvaffaqiyatli qo'shildi!", reply_markup=get_admin_menu_keyboard())
            
    await state.clear()

# --- MAHSULOT QO'SHISH FSM ---

@router.message(F.text == "➕ Mahsulot qo'shish", IsAdmin())
async def start_add_product(message: Message, state: FSMContext):
    keyboard = await get_admin_categories_keyboard()
    await message.answer("Mahsulot qaysi kategoriyaga tegishli? Tanlang:", reply_markup=keyboard)
    await state.set_state(AddProductState.category)

@router.callback_query(AddProductState.category, F.data.startswith("admincat_"), IsAdmin())
async def process_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])
    await state.update_data(category_id=category_id)
    
    await callback.message.answer("Endi mahsulotning rasmini yuboring 📸:")
    await state.set_state(AddProductState.image)
    await callback.answer()

@router.message(AddProductState.image, F.photo, IsAdmin())
async def process_image(message: Message, state: FSMContext):
    # Eng katta sifatdagi rasmni olamiz
    file_id = message.photo[-1].file_id
    await state.update_data(image_id=file_id)
    
    await message.answer("Mahsulot nomini yozing ✍️\n(Masalan: Rels 40 sm):")
    await state.set_state(AddProductState.name)

@router.message(AddProductState.name, F.text, IsAdmin())
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Mahsulot tavsifini yozing 📝\n(yoki 'yoq' deb yozib o'tkazib yuboring):")
    await state.set_state(AddProductState.description)

@router.message(AddProductState.description, F.text, IsAdmin())
async def process_description(message: Message, state: FSMContext):
    desc = message.text if message.text.lower() != 'yoq' else ""
    await state.update_data(description=desc)
    
    await message.answer("Mahsulot narxini so'mda yozing 💰\n(Faqat raqam, masalan: 15000):")
    await state.set_state(AddProductState.price)

@router.message(AddProductState.price, F.text, IsAdmin())
async def process_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, narxni faqat raqamlar bilan yozing!")
        return
        
    await state.update_data(price=float(message.text))
    await message.answer("Omborda bu mahsulotdan nechta bor? 📦\n(Masalan: 100):")
    await state.set_state(AddProductState.stock)

@router.message(AddProductState.stock, F.text, IsAdmin())
async def process_stock(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, sonini faqat raqamlar bilan yozing!")
        return
        
    data = await state.get_data()
    
    # Bazaga saqlaymiz
    async with async_session() as session:
        new_product = Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            stock=int(message.text),
            image_id=data['image_id'],
            category_id=data['category_id']
        )
        session.add(new_product)
        await session.commit()
        
    await state.clear()
    await message.answer(f"✅ Mahsulot muvaffaqiyatli qo'shildi!\nNomi: {data['name']}\nNarxi: {data['price']} so'm\nSoni: {message.text} ta", reply_markup=get_admin_menu_keyboard())

# --- OMBOR FSM ---

@router.message(F.text == "📉 Ombor", IsAdmin())
async def show_warehouse(message: Message, state: FSMContext):
    keyboard = await get_warehouse_keyboard()
    await message.answer("📉 Ombor holati:\nMahsulotni tanlab uning sonini o'zgartirishingiz mumkin:", reply_markup=keyboard)

@router.callback_query(F.data == "admin_add_product", IsAdmin())
async def call_add_product(callback: CallbackQuery, state: FSMContext):
    keyboard = await get_admin_categories_keyboard()
    await callback.message.edit_text("Mahsulot qaysi kategoriyaga tegishli? Tanlang:", reply_markup=keyboard)
    await state.set_state(AddProductState.category)
    await callback.answer()

@router.callback_query(F.data.startswith("manageprod_"), IsAdmin())
async def manage_product_choice(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    keyboard = get_manage_product_keyboard(product_id)
    await callback.message.edit_text("Ushbu mahsulotning nimasini o'zgartirmoqchisiz?", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith("editstock_"), IsAdmin())
async def start_edit_stock(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    await state.update_data(product_id=product_id)
    await callback.message.delete()
    await callback.message.answer("📦 Ushbu mahsulotning yangi sonini (qoldiqni) kiriting:")
    await state.set_state(EditStockState.new_stock)
    await callback.answer()

@router.message(EditStockState.new_stock, F.text, IsAdmin())
async def process_new_stock(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, sonni faqat raqam bilan yozing!")
        return
        
    data = await state.get_data()
    product_id = data['product_id']
    new_stock = int(message.text)
    
    async with async_session() as session:
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product:
            product.stock = new_stock
            await session.commit()
            
    await state.clear()
    await message.answer(f"✅ Mahsulot soni muvaffaqiyatli yangilandi: {new_stock} ta qoldi.", reply_markup=get_admin_menu_keyboard())

@router.callback_query(F.data.startswith("editprice_"), IsAdmin())
async def start_edit_price(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    await state.update_data(product_id=product_id)
    await callback.message.delete()
    await callback.message.answer("💰 Ushbu mahsulotning yangi narxini (so'mda) kiriting:\n(Faqat raqam yozing)")
    await state.set_state(EditPriceState.new_price)
    await callback.answer()

@router.message(EditPriceState.new_price, F.text, IsAdmin())
async def process_new_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Iltimos, narxni faqat raqam bilan yozing!")
        return
        
    data = await state.get_data()
    product_id = data['product_id']
    new_price = float(message.text)
    
    async with async_session() as session:
        result = await session.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        if product:
            product.price = new_price
            await session.commit()
            
    await state.clear()
    await message.answer(f"✅ Mahsulot narxi muvaffaqiyatli yangilandi: {new_price:,.0f} so'm bo'ldi.", reply_markup=get_admin_menu_keyboard())

# --- BUYURTMALARNI BOSHQARISH (TOPSHIRILDI / BEKOR QILISH) ---

@router.callback_query(F.data.startswith("order_complete_"), IsAdmin())
async def complete_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[2])
    
    async with async_session() as session:
        order = await session.get(Order, order_id)
        if order:
            order.status = OrderStatus.DELIVERED
            await session.commit()
            
            # Xabarni tahrirlash
            old_text = call.message.text
            new_text = old_text + "\n\n✅ **BU BUYURTMA TOPSHIRILDI!**"
            try:
                await call.message.edit_text(new_text, reply_markup=None)
            except Exception:
                pass
    
    await call.answer("Buyurtma topshirildi deb belgilandi!", show_alert=True)

@router.callback_query(F.data.startswith("order_cancel_"), IsAdmin())
async def cancel_order(call: CallbackQuery):
    order_id = int(call.data.split("_")[2])
    
    async with async_session() as session:
        order = await session.get(Order, order_id)
        if order and order.status != OrderStatus.REJECTED:
            order.status = OrderStatus.REJECTED
            
            # Mahsulotlarni omborga qaytarish
            stmt = select(OrderItem).where(OrderItem.order_id == order_id)
            result = await session.execute(stmt)
            order_items = result.scalars().all()
            
            for item in order_items:
                product = await session.get(Product, item.product_id)
                if product:
                    product.stock += item.quantity
                    
            await session.commit()
            
            # Xabarni tahrirlash
            old_text = call.message.text
            new_text = old_text + "\n\n❌ **BU BUYURTMA BEKOR QILINDI! (Mahsulotlar omborga qaytarildi)**"
            try:
                await call.message.edit_text(new_text, reply_markup=None)
            except Exception:
                pass
                
    await call.answer("Buyurtma bekor qilindi va mahsulotlar omborga qaytdi!", show_alert=True)

# --- STATISTIKA ---

@router.message(F.text == "📊 Statistika", IsAdmin())
async def show_statistics(message: Message):
    async with async_session() as session:
        # Foydalanuvchilar soni
        users_count = await session.scalar(select(func.count()).select_from(User))
        
        # Jami buyurtmalar soni
        orders_count = await session.scalar(select(func.count()).select_from(Order))
        
        # Jami savdo summasi (Yopilgan / Yetkazib berilgan buyurtmalar asosida)
        result = await session.execute(select(func.sum(Order.total_price)).where(Order.status == OrderStatus.DELIVERED))
        total_revenue = result.scalar() or 0
        
    text = (
        "📊 **Bot Statistikasi:**\n\n"
        f"👥 Umumiy foydalanuvchilar: **{users_count} ta**\n"
        f"📦 Barcha buyurtmalar: **{orders_count} ta**\n"
        f"💰 Jami tasdiqlangan savdo: **{total_revenue:,.0f} so'm**"
    )
    await message.answer(text, parse_mode="Markdown")

# --- OMMAVIY XABAR (REKLAMA) YUBORISH ---

@router.message(F.text == "📣 Reklama yuborish", IsAdmin())
async def start_broadcast(message: Message, state: FSMContext):
    await message.answer("Barcha bot foydalanuvchilariga yubormoqchi bo'lgan xabaringizni yuboring.\n*(Matn, rasm, video — istalgan format qabul qilinadi)*\n\nJarayonni bekor qilish uchun '⬅️ Mijoz menyusi' ni bosing.", parse_mode="Markdown")
    await state.set_state(BroadcastState.waiting_for_message)

@router.message(BroadcastState.waiting_for_message, IsAdmin())
async def process_broadcast(message: Message, state: FSMContext):
    if message.text == "⬅️ Mijoz menyusi":
        await state.clear()
        await message.answer("Reklama yuborish bekor qilindi.", reply_markup=get_main_menu_keyboard())
        return

    await state.clear()
    msg = await message.answer("⏳ Reklama yuborish boshlandi. Iltimos kuting...")
    
    success = 0
    failed = 0
    
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        for user in users:
            try:
                await message.send_copy(chat_id=user.id)
                success += 1
            except Exception:
                failed += 1
                
    await msg.delete()
    await message.answer(
        f"✅ **Reklama yuborish yakunlandi!**\n\n"
        f"📩 Muvaffaqiyatli yuborildi: {success} ta foydalanuvchiga\n"
        f"🚫 Xatolik (botni bloklaganlar): {failed} ta",
        parse_mode="Markdown",
        reply_markup=get_admin_menu_keyboard()
    )
