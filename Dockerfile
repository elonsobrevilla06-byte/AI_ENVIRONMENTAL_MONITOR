FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1. Install standard requirements from PyPI
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Install PyTorch and torchvision from the official PyTorch CUDA index
# This command specifically targets the index for your torch versions
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu126

# Copy the rest of your app code
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]