import asyncio
import os
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from aiogram import Bot

from config.config import BOT_TOKEN
from database.engine import async_session
from database.models import Category, Product
from sqlalchemy import select

web_bot = Bot(token=BOT_TOKEN)
app = FastAPI()

@app.on_event("shutdown")
async def shutdown_event():
    await web_bot.session.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the webapp directory as static files
app.mount("/static", StaticFiles(directory="webapp"), name="static")

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
    file_path = f"downloads/{file_id}.jpg"
    if not os.path.exists(file_path):
        os.makedirs("downloads", exist_ok=True)
        try:
            file = await web_bot.get_file(file_id)
            await web_bot.download_file(file.file_path, file_path)
        except Exception as e:
            return Response(status_code=404)
            
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return Response(status_code=404)

async def run_web_app():
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()
