import os, sys


def read(path):
    with open(path, "r") as f:
        return f.read()


def write(path, content):
    with open(path, "w") as f:
        f.write(content.strip() + "\n")
    print(f"  Written: {path}")


print("1. Fixing corrupted Python files...")
for f in [
    "hotel/public_views.py",
    "hotel/inventory/services.py",
    "hotel/content/views.py",
]:
    try:
        c = read(f)
        c = c.strip('"').strip("'").strip()
        write(f, c)
    except Exception as e:
        print(f"  Error: {f} - {e}")

print("\n2. Creating Celery config...")
write(
    "config/celery.py",
    """import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = Celery("hotel")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
""",
)

print("\n3. Creating docker/entrypoint.sh...")
os.makedirs("docker", exist_ok=True)
write(
    "docker/entrypoint.sh",
    """#!/bin/bash
set -e

echo "=== Il Mercato Hotel - Starting ==="

# Apply database migrations
python manage.py migrate --noinput

# Create superuser if needed
if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput --email "$DJANGO_SUPERUSER_EMAIL" 2>/dev/null || true
fi

echo "=== Starting application ==="
exec "$@"
""",
)

print("\n4. Fixing Dockerfile...")
dockerfile = read("Dockerfile")
write("Dockerfile", dockerfile.strip('"').strip())

print("\n5. Verifying models import...")
sys.path.insert(0, ".")
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"
os.environ.setdefault("DATABASE_URL", "postgres://sonto:sonto@localhost:5433/hotel")

import django

django.setup()

from hotel.rooms.models import RoomType, Amenity, Room, RoomTypeImage
from hotel.inventory.models import (
    Season,
    MealPlan,
    RateRule,
    InventoryAllotment,
    StopSell,
)
from hotel.guests.models import Guest
from hotel.bookings.models import BookingCart, Booking, BookingVersion, BookingRoom
from hotel.payments.models import Payment, Refund, WebhookEvent
from hotel.notifications.models import EmailTemplate, EmailLog
from hotel.content.models import (
    SiteSettings,
    HeroSlide,
    GalleryImage,
    Offer,
    Review,
    NewsletterSubscriber,
)

print("  All models import OK")

print("\n=== Setup complete ===")
print("\nTo run locally with Docker:")
print("  docker compose up -d --build")
print("\nTo push to Docker Hub:")
print("  docker build -t yourusername/ilmercatohotel:latest .")
print("  docker push yourusername/ilmercatohotel:latest")
