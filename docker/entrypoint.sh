#!/bin/bash
set -e

echo "=== Il Mercato Hotel - Starting ==="

# Create placeholder font files if they don't exist (for collectstatic)
mkdir -p /app/hotel/static/fonts
for font in inter-regular inter-medium inter-semibold inter-bold playfair-display-regular playfair-display-italic playfair-display-medium playfair-display-semibold playfair-display-bold; do
    if [ ! -f "/app/hotel/static/fonts/${font}.woff2" ]; then
        echo "placeholder" > "/app/hotel/static/fonts/${font}.woff2"
    fi
done

# Collect static files (WhiteNoise with manifest storage)
python manage.py collectstatic --noinput

# Compress static files (django-compressor offline mode)
python manage.py compress --force 2>/dev/null || true

# Apply database migrations
python manage.py migrate --noinput

# Create superuser if credentials provided
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput --email "$DJANGO_SUPERUSER_EMAIL" 2>/dev/null || true
fi

echo "=== Starting application ==="
exec "$@"
