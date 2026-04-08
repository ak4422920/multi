# 1. Base image (Python 3.11)
FROM python:3.11-slim

# 2. System dependencies
# Added 'aria2' for Magnets/Direct links
# Added 'ffmpeg' (optional but recommended for yt-dlp to merge audio/video)
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    aria2 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 3. Deno Install (YouTube 'n-challenge' solve karne ke liye zaroori hai)
RUN curl -fsSL https://deno.land/install.sh | sh
ENV DENO_INSTALL="/root/.deno"
ENV PATH="$DENO_INSTALL/bin:$PATH"

# 4. Working directory
WORKDIR /app

# 5. Copy your files
COPY . .

# 6. Install Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# 7. Start the bot
CMD ["python", "main.py"]