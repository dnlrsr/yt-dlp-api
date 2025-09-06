FROM python:3.11-slim

RUN apt update && apt install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install yt-dlp

# Create cache directory and set up user home directory
RUN mkdir -p /home/appuser/.cache/yt-dlp && \
    chown -R 1000:1000 /home/appuser

# Copy application code
COPY . /app
WORKDIR /app

# Copy requirements and install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /data/youtube
RUN mkdir -p /data/downloads
RUN chown -R 1000:1000 /data/youtube /data/downloads

# Switch to non-root user and set environment variables
RUN touch api_token.txt
RUN chown -R 1000:1000 api_token.txt

USER 1000:1000

ENV XDG_CACHE_HOME=/home/appuser/.cache
ENV HOME=/home/appuser
ENV DOCKERIZED=true

EXPOSE 5000

# Use Gunicorn for production
ENV PYTHONUNBUFFERED=1
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--timeout", "300", "--log-level", "info", "wsgi:app"]

