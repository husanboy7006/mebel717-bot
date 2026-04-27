import asyncio
import logging
from aiogram import Bot, Dispatcher
from config.config import BOT_TOKEN
from handlers import user_handlers, shop_handlers, admin_handlers
from database.engine import init_db
from database.seed import seed_categories
from web import run_web_app

# Loglarni sozlash (Bot qanday ishlayotganini ko'rib turish uchun)
logging.basicConfig(level=logging.INFO)

async def main():
    # Baza jadvallarini yaratish (agar yo'q bo'lsa)
    try:
        await init_db()
        await seed_categories() # Kategoriyalarni bazaga qo'shish
        logging.info("Ma'lumotlar bazasiga muvaffaqiyatli ulandi va jadvallar tekshirildi.")
    except Exception as e:
        logging.error(f"Bazaga ulanishda xatolik: {e}\nIltimos, .env dagi DB_URL ni tekshiring!")

    # Tokenni tekshiramiz
    if not BOT_TOKEN or BOT_TOKEN == "1234567890:YOUR_BOT_TOKEN_HERE":
        logging.error("Iltimos, .env faylida BOT_TOKEN ni o'rnating!")
        return

    # Bot va Dispatcher ob'ektlarini yaratish
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Handlerlarni ro'yxatdan o'tkazish
    dp.include_router(admin_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(shop_handlers.router)

    # Web App serverini fonda ishga tushirish
    asyncio.create_task(run_web_app())

    # Botni ishga tushirish (Polling)
    logging.info("Bot ishga tushdi...")
    
    # Eski xabarlarni o'tkazib yuborish (ixtiyoriy)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Pollingni boshlash
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")
