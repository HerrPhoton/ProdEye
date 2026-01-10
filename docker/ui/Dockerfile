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

    # X11
    libx11-6 \
    libxext6 \
    libxrender1 \

    # Qt6 platform (xcb)
    libxkbcommon0 \
    libxcb1 \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libfontconfig1 \
    libfreetype6 \
    fonts-dejavu-core \
    libdbus-1-3 \

    # FFmpeg
    ffmpeg \

    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt .
COPY requirements/ui.txt .

RUN pip install --no-cache-dir -r ui.txt

COPY src/ ./src/

CMD ["python", "-m", "src.ui_main"]
