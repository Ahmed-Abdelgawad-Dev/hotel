# ─── Production Dockerfile for Il Mercato Hotel ───
# Multi-stage: Python 3.14 + Django + WhiteNoise + PostgreSQL + Redis


FROM python:3.14 AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential libpq-dev libjpeg62-turbo-dev libtiff5-dev \
  libwebp-dev zlib1g-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir \
  django==5.2.9 django-allauth[mfa]==65.13.1 django-anymail==14.0 \
  django-compressor==4.6.0 django-crispy-forms==2.5 crispy-bootstrap5==2025.6 \
  django-environ==0.12.0 django-redis==6.0.0 django-ratelimit==4.1.0 \
  django-debug-toolbar==6.1.0 django-extensions==4.1 gunicorn==23.0.0 \
  whitenoise==6.11.0 psycopg[binary]==3.3.2 pillow==12.0.0 redis==7.1.0 \
  celery==5.6.3 argon2-cffi==25.1.0 python-slugify==8.0.4


FROM python:latest

LABEL maintainer="Ahmed Abdelgawad <ahmed.abdelgawad.dev@gmail.com>"
LABEL org.opencontainers.image.title="Il Mercato Hotel"
LABEL org.opencontainers.image.description="Hotel Booking Engine"
LABEL org.opencontainers.image.version="1.0"

RUN apt-get update && apt-get install -y --no-install-recommends \
  libpq-dev libjpeg62-turbo libtiff6 libwebp7 curl && rm -rf /var/lib/apt/lists/*

RUN groupadd -r hotel && useradd -r -g hotel -d /app -s /sbin/nologin hotel

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

RUN mkdir -p /app/staticfiles /app/media && chown -R hotel:hotel /app

COPY docker/entrypoint.sh /entrypoint.sh
COPY docker/entrypoint-celery.sh /entrypoint-celery.sh
RUN chmod +x /entrypoint.sh /entrypoint-celery.sh

USER hotel

ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  DJANGO_SETTINGS_MODULE=config.settings.production

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--access-logfile", "-"]
