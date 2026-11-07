FROM python:3.12-slim

# Ngăn Python tạo bytecode .pyc và bật stdout unbuffered để xem log ngay lập tức
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Cài đặt dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn bot
COPY . .

# Khởi chạy bot
CMD ["python", "bot.py"]
