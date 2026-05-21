import asyncio
import os
import hashlib
import hmac
import json
import time
from contextlib import asynccontextmanager
from urllib.parse import parse_qsl

from fastapi import FastAPI, Response, Header, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from aiogram import Bot

from config.config import BOT_TOKEN, ADMIN_IDS
from database.engine import async_session
from database.models import Category, Product
from sqlalchemy import select

web_bot = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global web_bot
    web_bot = Bot(token=BOT_TOKEN)
    yield
    if web_bot:
        await web_bot.session.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="webapp"), name="static")


def verify_admin(init_data: str) -> dict:
    """Telegram initData ni tekshirib, admin ekanligini tasdiqlaydi"""
    try:
        parsed = dict(parse_qsl(init_data, keep_blank_values=True))
        hash_val = parsed.pop('hash', None)
        if not hash_val:
            raise HTTPException(status_code=403, detail="initData topilmadi")

        # Imzoni tekshirish
        data_check = '\n'.join(f"{k}={v}" for k, v in sorted(parsed.items()))
        secret = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        expected = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(expected, hash_val):
            raise HTTPException(status_code=403, detail="Imzo noto'g'ri")

        # Vaqt tekshiruvi (1 soat)
        auth_date = int(parsed.get('auth_date', 0))
        if time.time() - auth_date > 3600:
            raise HTTPException(status_code=403, detail="Sessiya muddati o'tgan")

        # Admin tekshiruvi
        user = json.loads(parsed.get('user', '{}'))
        if user.get('id') not in ADMIN_IDS:
            raise HTTPException(status_code=403, detail="Ruxsat yo'q")

        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=403, detail="initData xato")


class UpdateRequest(BaseModel):
    product_id: int
    field: str
    value: float


# --- Mijoz API ---

@app.get("/api/data")
async def get_data():
    async with async_session() as session:
        cat_result = await session.execute(select(Category))
        categories = cat_result.scalars().all()
        prod_result = await session.execute(select(Product).where(Product.stock > 0))
        products = prod_result.scalars().all()
        return {
            "categories": [{"id": c.id, "name": c.name} for c in categories],
            "products": [{"id": p.id, "category_id": p.category_id, "name": p.name, "description": p.description, "price": p.price, "stock": p.stock, "image_id": p.image_id} for p in products]
        }

@app.get("/api/image/{file_id}")
async def get_image(file_id: str):
    if not web_bot:
        return Response(status_code=503)
    file_path = f"downloads/{file_id}.jpg"
    if not os.path.exists(file_path):
        os.makedirs("downloads", exist_ok=True)
        try:
            file = await web_bot.get_file(file_id)
            await web_bot.download_file(file.file_path, file_path)
        except Exception:
            return Response(status_code=404)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return Response(status_code=404)


# --- Admin API ---

@app.get("/api/admin/products")
async def get_admin_products(x_init_data: str = Header(None)):
    if not x_init_data:
        raise HTTPException(status_code=403, detail="initData kerak")
    verify_admin(x_init_data)

    async with async_session() as session:
        cat_result = await session.execute(select(Category))
        categories = cat_result.scalars().all()
        prod_result = await session.execute(
            select(Product).order_by(Product.category_id, Product.name)
        )
        products = prod_result.scalars().all()

    return {
        "categories": [{"id": c.id, "name": c.name} for c in categories],
        "products": [{"id": p.id, "category_id": p.category_id, "name": p.name, "description": p.description, "price": p.price, "stock": p.stock, "image_id": p.image_id} for p in products]
    }


@app.post("/api/admin/update")
async def update_product(req: UpdateRequest, x_init_data: str = Header(None)):
    if not x_init_data:
        raise HTTPException(status_code=403, detail="initData kerak")
    verify_admin(x_init_data)

    if req.field not in ("stock", "price"):
        raise HTTPException(status_code=400, detail="Noto'g'ri maydon")

    async with async_session() as session:
        product = await session.get(Product, req.product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
        if req.field == "stock":
            product.stock = int(req.value)
        else:
            product.price = float(req.value)
        await session.commit()

    return {"ok": True}


async def run_web_app():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
