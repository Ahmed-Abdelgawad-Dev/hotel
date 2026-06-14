#!/bin/bash
set -e

echo "=== Il Mercato Hotel - Celery Worker Starting ==="

# Wait for web to run migrations first (sleep a bit)
sleep 5

echo "=== Starting Celery ==="
exec "$@"
