# Mebel Furnitura Telegram Bot & Mini App

Zamonaviy mebel furnituralari do'koni uchun yaratilgan professional Telegram bot va integratsiya qilingan Mini App (WebApp) platformasi. Loyiha mijozlar uchun qulay savdo interfeysi va adminlar uchun kuchli boshqaruv tizimini taqdim etadi.

## 🚀 Asosiy Funksiyalar

### 📱 Mijozlar uchun:
*   **Telegram Mini App**: To'liq interaktiv va tezkor mahsulotlar katalogi.
*   **Aqlli Qidiruv**: Mahsulot nomi va tavsifi bo'yicha lahzali qidiruv tizimi.
*   **Savatcha Tizimi**: WebApp ichida joylashgan "Sticky Bottom Bar" orqali savatchani boshqarish.
*   **Buyurtma berish**: Lokatsiya yuborish va to'lov turini tanlash imkoniyati.
*   **Buyurtmalar tarixi**: Mijoz o'zining barcha buyurtmalarini bot orqali kuzatib borishi mumkin.

### ⚙️ Adminlar uchun:
*   **Katalog boshqaruvi**: Bot orqali kategoriya va mahsulotlarni qo'shish/o'chirish.
*   **Buyurtmalar nazorati**: Yangi buyurtmalar haqida admin guruhiga lahzali xabarnoma yuborish.
*   **Statistika**: Savdo va mijozlar haqida statistik ma'lumotlar.
*   **Ombor boshqaruvi**: Mahsulotlar qoldig'ini nazorat qilish.

## 🛠 Texnologik Stek

*   **Backend**: Python 3.11, Aiogram 3.x (Telegram Framework).
*   **API/Web**: FastAPI (WebApp ma'lumotlarini yetkazib berish uchun).
*   **Database**: SQLite + SQLAlchemy (Asyncio).
*   **Frontend**: Vanilla JavaScript, CSS3 (Telegram WebApp standardlariga mos).
*   **Infrastructure**: Docker, Docker-compose, Caddy (Reverse Proxy & SSL).

## 📂 Loyiha Tuzilishi

```
mebel/
├── bot.py                # Botning asosiy kirish nuqtasi
├── web.py                # FastAPI server (API & Static files)
├── config/               # Konfiguratsiya va .env yuklagich
├── database/             # MB modellari va ulanish (SQLAlchemy)
├── handlers/             # Bot buyruqlari va mantiqi
├── keyboards/            # Telegram tugmalari (Reply/Inline)
├── utils/                # Yordamchi funksiyalar va holatlar (States)
├── webapp/               # Mini App frontend qismi (HTML/CSS/JS)
├── Dockerfile            # Konteyner sozlamalari
└── docker-compose.yml    # Servislarni boshqarish
```

## ⚙️ O'rnatish va Ishga tushirish

1.  **Loyiha nusxasini yuklab oling**:
    ```bash
    git clone https://github.com/husanboy7006/mebel717-bot.git
    cd mebel717-bot
    ```

2.  **Muhit o'zgaruvchilarini sozlang**:
    `.env` faylini yarating va quyidagilarni kiriting:
    ```env
    BOT_TOKEN=sizning_bot_tokeningiz
    ADMIN_IDS=admin_id1,admin_id2
    DB_URL=sqlite+aiosqlite:///mebel.db
    GROUP_ID=admin_guruhi_id
    ```

3.  **Docker orqali ishga tushiring**:
    ```bash
    docker-compose up -d --build
    ```

## 🔐 Xavfsizlik bo'yicha eslatma

Loyiha xavfsizligini ta'minlash uchun:
*   Bot tokenini hech qachon kod ichida (hardcoded) qoldirmang.
*   `.env` va `logs.txt` fayllarini `.gitignore` orqali yashiring.
*   Serverga kirishda faqat ishonchli SSH kalitlaridan foydalaning.

## 📄 Litsenziya
Ushbu loyiha shaxsiy foydalanish va o'rganish uchun yaratilgan.

---
**Dasturchi**: Antigravity AI Assistant
**Versiya**: 3.2.0
