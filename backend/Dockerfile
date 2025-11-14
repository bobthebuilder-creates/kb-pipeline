FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable buffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (optional: for later PDF parsing, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src ./src

# Environment
ENV APP_PORT=7777

EXPOSE 7777

CMD ["python", "-m", "src.api.main"]
