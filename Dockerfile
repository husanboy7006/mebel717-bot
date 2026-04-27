# Asosiy rasm sifatida yengil va tezkor Python 3.11-slim versiyasini tanlaymiz
FROM python:3.11-slim

# Konteyner ichidagi ishchi papkani belgilaymiz
WORKDIR /app

# Atrof-muhit o'zgaruvchilarini sozlaymiz (Python va pip loglarini optimallashtirish uchun)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Kerakli tizim paketlarini o'rnatamiz (kerak bo'lsa)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# requirements.txt faylini nusxalab, modullarni o'rnatamiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Qolgan barcha loyiha fayllarini konteynerga nusxalaymiz
COPY . .

# FastAPI ishlashi uchun kerak bo'lgan portni ochamiz
EXPOSE 8000

# Botni ishga tushirish komandasi
CMD ["python", "bot.py"]
