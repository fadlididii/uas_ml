# ---- Base Image ----
FROM python:3.11-slim

# ---- Set Work Directory ----
WORKDIR /app

# ---- Install System Dependencies ----
# Only what is needed for runtime + opencv-headless
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgtk-3-dev \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# ---- Install Python Dependencies ----
# Use --no-cache-dir and avoid COPYing models into image
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- Copy App Code (excluding large models) ----
COPY . .

# ---- Set Environment Variables ----
ENV PYTHONUNBUFFERED=1

# ---- Default Command (adjust if needed) ----
CMD ["python", "app.py"]
