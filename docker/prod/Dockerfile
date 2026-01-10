FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    # OpenGL / OpenCV
    libgl1 \
    libegl1 \
    libgles2 \
    libglx-mesa0 \
    libglib2.0-0 \

    # FFmpeg
    ffmpeg \

    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt .
RUN pip install --no-cache-dir -r base.txt

COPY src ./src

CMD ["python", "-m", "src.main"]
