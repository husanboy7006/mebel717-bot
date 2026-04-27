import asyncio
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from config.config import BOT_TOKEN, ADMIN_IDS

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))

async def send():
    admin_text = "🔥 <b>YANGI BUYURTMA #1</b>\n\n👤 Haridor: HUSAN\n📱 Tel: O'zim olib ketaman\n📍 Manzil: fg cffc\n💳 To'lov turi: Karta\n\n📦 <b>Mahsulotlar:</b>\n1. O'zbekiston mahsuloti (Test)\n\n💰 <b>Jami: 15,000 so'm</b>\n\n<i>(Bu tizimni tekshirish uchun adminga qayta yuborilgan xabar)</i>"
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text)
            print("Yuborildi")
        except Exception as e:
            print(f"Xato: {e}")
            await bot.send_message(admin_id, admin_text, parse_mode=None)

    await bot.session.close()

asyncio.run(send())
