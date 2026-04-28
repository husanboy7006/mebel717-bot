import json
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext

from keyboards.reply import get_main_menu_keyboard, get_contact_keyboard, get_payment_keyboard, get_address_keyboard
from keyboards.inline import get_order_admin_keyboard
from utils.states import CheckoutState
from config.config import ADMIN_IDS, GROUP_ID
from database.engine import async_session
from database.models import Order, OrderItem, Product, User
from sqlalchemy import select

router = Router()

@router.message(Command("id"))
async def cmd_id(message: Message):
    """Foydalanuvchi o'z Telegram ID sini bilishi uchun"""
    await message.answer(f"👤 Sizning ID raqamingiz: `{message.from_user.id}`\n💬 Guruh/Chat ID raqami: `{message.chat.id}`", parse_mode="Markdown")

@router.message(CommandStart())
async def cmd_start(message: Message):
    """/start komandasiga javob va bazaga user qo'shish"""
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == message.from_user.id))
        user = result.scalar_one_or_none()
        
        if not user:
            new_user = User(
                id=message.from_user.id,
                full_name=message.from_user.full_name,
                phone_number=None
            )
            session.add(new_user)
            await session.commit()

    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\n"
        f"Mebel furnitura do'konimizga xush kelibsiz.\n"
        f"Quyidagi menyu orqali o'zingizga kerakli bo'limni tanlang:",
        reply_markup=get_main_menu_keyboard()
    )

@router.message(F.text == "☎️ Aloqa")
async def contact_handler(message: Message):
    """Aloqa tugmasi bosilganda"""
    text = (
        "📞 Biz bilan bog'lanish uchun:\n\n"
        "📱 Telefon: +998 90 123 45 67\n"
        "📩 Telegram admin: @admin_username\n"
        "📍 Manzil: Toshkent shahar, Chilonzor tumani..."
    )
    await message.answer(text)

@router.message(F.text == "🚚 Yetkazib berish")
async def delivery_info_handler(message: Message):
    """Yetkazib berish info tugmasi"""
    text = (
        "🚚 Yetkazib berish xizmati:\n\n"
        "🏢 O'zingiz olib ketish - 0 so'm (Bepul)\n"
        "🚕 Toshkent shahar bo'ylab - Yandex narxlari asosida manzilga qarab hisoblanadi.\n\n"
        "Buyurtma qabul qilingach, adminlarimiz yetkazib berish narxini siz bilan kelishishadi."
    )
    await message.answer(text)

# --- CHECKOUT LOGIC (Web App dan ma'lumot qabul qilish) ---

@router.message(F.content_type == ContentType.WEB_APP_DATA)
async def handle_web_app_data(message: Message, state: FSMContext):
    """Web App dan buyurtma ro'yxati kelganda ishlash"""
    try:
        data = json.loads(message.web_app_data.data)
    except Exception:
        await message.answer("Xatolik yuz berdi. Qaytadan urinib ko'ring.")
        return

    if not data:
        await message.answer("Savat bo'sh.")
        return
        
    true_cart = []
    total_price = 0
    
    async with async_session() as session:
        for item in data:
            product_id = item['product']['id']
            quantity = item['quantity']
            
            product = await session.get(Product, product_id)
            if product and product.stock >= quantity:
                item_price = product.price
                total_price += item_price * quantity
                true_cart.append({
                    'product': {'id': product.id, 'name': product.name, 'price': item_price},
                    'quantity': quantity
                })
            else:
                await message.answer(f"⚠️ Kechirasiz, '{item['product']['name']}' mahsulotidan omborda yetarli qolmagan yoki o'chirilgan.")
                return

    if not true_cart:
        return
        
    # Ma'lumotni state da saqlash
    await state.update_data(cart=true_cart, total_price=total_price)
    data = true_cart # formatlash uchun
    
    text = "🛒 **Sizning buyurtmangiz:**\n\n"
    for i, item in enumerate(data, 1):
        p = item['product']
        q = item['quantity']
        text += f"{i}. {p['name']} | {q} ta x {p['price']:,.0f} = {p['price']*q:,.0f} so'm\n"
    
    text += f"\n💰 **Umumiy summa: {total_price:,.0f} so'm**\n"
    text += "🚚 *Yetkazib berish narxi: Manzilga qarab kelishiladi*\n\n"
    text += "Buyurtmani rasmiylashtirish uchun, pastdagi **📱 Telefon raqamni yuborish** tugmasini bosing:"
    
    await message.answer(text, reply_markup=get_contact_keyboard(), parse_mode="Markdown")
    await state.set_state(CheckoutState.waiting_for_phone)

@router.message(CheckoutState.waiting_for_phone, F.contact | F.text)
async def process_phone(message: Message, state: FSMContext):
    """Telefon raqami qabul qilinganda"""
    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text
        
    await state.update_data(phone=phone)
    await message.answer(
        "📍 Endi **yetkazib berish manzilini** kiriting yoki xaritadan jo'nating:\n"
        "(O'zingiz olib ketmoqchi bo'lsangiz quyidagi tugmani bosing)", 
        reply_markup=get_address_keyboard()
    )
    await state.set_state(CheckoutState.waiting_for_address)

@router.message(CheckoutState.waiting_for_address, F.location | F.text)
async def process_address(message: Message, state: FSMContext):
    """Manzil yoki lokatsiya qabul qilinganda"""
    if message.location:
        address = f"📍 Lokatsiya: {message.location.latitude}, {message.location.longitude}"
    else:
        address = message.text
        
    await state.update_data(address=address)
    
    await message.answer("💳 Iltimos, **to'lov turini** tanlang:", reply_markup=get_payment_keyboard())
    await state.set_state(CheckoutState.waiting_for_payment)

@router.message(CheckoutState.waiting_for_payment, F.text)
async def process_payment(message: Message, state: FSMContext):
    """To'lov turi qabul qilingach, buyurtmani bazaga yozish va Adminga yuborish"""
    payment = message.text
    user_data = await state.get_data()
    
    cart = user_data.get('cart', [])
    total_price = user_data.get('total_price', 0)
    phone = user_data.get('phone', 'Noma\'lum')
    address = user_data.get('address', 'Noma\'lum')
    
    # 1. Bazaga saqlash
    async with async_session() as session:
        from database.models import OrderStatus
        new_order = Order(
            user_id=message.from_user.id,
            total_price=total_price,
            status=OrderStatus.PENDING,
            phone_number=phone,
            address=address,
            delivery_type="Kuryer orqali yoki olib ketish",
            payment_type=payment
        )
        session.add(new_order)
        await session.flush() # new_order.id ni olish uchun
        
        for item in cart:
            p_data = item['product']
            q = item['quantity']
            
            # Buyurtma elementini qo'shish
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=p_data['id'],
                quantity=q,
                price=p_data['price']
            )
            session.add(order_item)
            
            # Ombordan ayirib tashlash (Stokdan minus qilish)
            product = await session.get(Product, p_data['id'])
            if product and product.stock >= q:
                product.stock -= q
                
        await session.commit()
        order_id = new_order.id

    # 2. Adminga xabar yuborish
    admin_text = (
        f"🔥 **YANGI BUYURTMA #{order_id}**\n\n"
        f"👤 Haridor: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"📱 Tel: {phone}\n"
        f"📍 Manzil: {address}\n"
        f"💳 To'lov turi: {payment}\n\n"
        f"📦 **Mahsulotlar:**\n"
    )
    for i, item in enumerate(cart, 1):
        p = item['product']
        q = item['quantity']
        admin_text += f"{i}. {p['name']} | {q} ta = {p['price']*q:,.0f} so'm\n"
    
    admin_text += f"\n💰 **Jami summa: {total_price:,.0f} so'm**\n"
    admin_text += "🚚 *Yetkazib berish: Alohida hisoblanadi*"
    
    bot = message.bot
    keyboard = get_order_admin_keyboard(order_id)
    
    targets = [GROUP_ID] if GROUP_ID else ADMIN_IDS
    for target in targets:
        if not target: continue
        try:
            await bot.send_message(target, admin_text, parse_mode="Markdown", reply_markup=keyboard)
        except Exception as e:
            try:
                # Agar Markdown xato bersa, oddiy text sifatida jo'natadi
                await bot.send_message(target, admin_text, reply_markup=keyboard)
            except Exception:
                pass
        
        # Agar manzil lokatsiya bo'lsa, xaritani ham yuboramiz
        if address.startswith("📍 Lokatsiya: "):
            try:
                coords = address.replace("📍 Lokatsiya: ", "").split(", ")
                lat = float(coords[0])
                lon = float(coords[1])
                await bot.send_location(chat_id=target, latitude=lat, longitude=lon)
            except Exception:
                pass
            
    # 3. Foydalanuvchiga tasdiq xabari
    if payment == "💳 Karta (Click/Payme)":
        await state.update_data(order_id=order_id)
        await message.answer(
            f"✅ **Buyurtmangiz (#{order_id}) saqlandi!**\n\n"
            f"Siz **Click / Payme** orqali to'lovni tanladingiz.\n"
            f"Iltimos, pastdagi karta raqamiga **{total_price:,.0f} so'm** o'tkazing:\n\n"
            f"💳 Karta: `5614 6803 0182 1680`\n"
            f"👤 Qabul qiluvchi: Mebel do'koni admini\n\n"
            f"To'lovni amalga oshirgach, tasdiqlash uchun shu yerga **to'lov chekini (skrinshotini) yuboring** 📸:",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode="Markdown"
        )
        await state.set_state(CheckoutState.waiting_for_receipt)
    else:
        await state.clear()
        await message.answer(
            f"✅ **Buyurtmangiz muvaffaqiyatli qabul qilindi! (Buyurtma raqami: #{order_id})**\n\n"
            "Tez orada menejerlarimiz siz bilan bog'lanib, **yetkazib berish summasini** aytishadi va buyurtmani tasdiqlashadi. Xaridingiz uchun rahmat!",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )

@router.message(CheckoutState.waiting_for_receipt, (F.photo | F.document))
async def process_receipt(message: Message, state: FSMContext):
    """Mijoz yuborgan chekni qabul qilib, adminga yuborish"""
    user_data = await state.get_data()
    order_id = user_data.get('order_id')

    # Adminga yuboramiz
    bot = message.bot
    admin_text = f"💳 **#{order_id} buyurtma uchun to'lov cheki keldi!**\n\nMijoz: {message.from_user.full_name} (@{message.from_user.username})"
    
    targets = [GROUP_ID] if GROUP_ID else ADMIN_IDS
    
    if message.photo:
        file_id = message.photo[-1].file_id
        for target in targets:
            if not target: continue
            try:
                await bot.send_photo(target, photo=file_id, caption=admin_text, parse_mode="Markdown")
            except Exception:
                try:
                    await bot.send_photo(target, photo=file_id, caption=admin_text)
                except Exception:
                    pass
    elif message.document:
        file_id = message.document.file_id
        for target in targets:
            if not target: continue
            try:
                await bot.send_document(target, document=file_id, caption=admin_text, parse_mode="Markdown")
            except Exception:
                try:
                    await bot.send_document(target, document=file_id, caption=admin_text)
                except Exception:
                    pass

    await state.clear()
    await message.answer(
        "✅ **Chek qabul qilindi! Katta rahmat.**\n\n"
        "Adminlarimiz to'lovni tasdiqlashlari bilan buyurtmangiz tayyorlanadi va yetkazib berish bo'yicha siz bilan bog'lanamiz.",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )

@router.message(CheckoutState.waiting_for_receipt)
async def invalid_receipt(message: Message):
    """Mijoz rasm o'rniga tekst yozib yuborsa"""
    await message.answer("Iltimos, to'lovni tasdiqlash uchun **chekni rasm qilib (skrinshot)** yuboring! 📸")
