from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.web_app_info import WebAppInfo

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu tugmalari"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Mahsulotlar", web_app=WebAppInfo(url="https://mebel717.uz/static/index.html?v=2.0.0"))],
            [KeyboardButton(text="🛒 Savat"), KeyboardButton(text="📦 Buyurtmalarim")],
            [KeyboardButton(text="🚚 Yetkazib berish"), KeyboardButton(text="☎️ Aloqa")]
        ],
        resize_keyboard=True, # Tugmalar hajmini ekranga moslash
        input_field_placeholder="Quyidagi menyudan tanlang..."
    )
    return keyboard

def get_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """Admin menyusi tugmalari"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Mahsulot qo'shish"), KeyboardButton(text="📁 Kategoriya qo'shish")],
            [KeyboardButton(text="📦 Buyurtmalar"), KeyboardButton(text="📉 Ombor")],
            [KeyboardButton(text="📣 Reklama yuborish"), KeyboardButton(text="📊 Statistika")],
            [KeyboardButton(text="⬅️ Mijoz menyusi")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Admin menyusi..."
    )
    return keyboard

def get_contact_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqam so'rash klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_payment_keyboard() -> ReplyKeyboardMarkup:
    """To'lov turini so'rash klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💵 Naqd"), KeyboardButton(text="💳 Karta (Click/Payme)")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_address_keyboard() -> ReplyKeyboardMarkup:
    """Lokatsiya so'rash klaviaturasi"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Lokatsiyani yuborish", request_location=True)],
            [KeyboardButton(text="O'zim olib ketaman")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
