#!/usr/bin/env bash
set -o errexit
set -o pipefail

if [ ! -f manage.py ]; then
  echo "Run this from the Django project root (manage.py not found)." >&2
  exit 1
fi

python_bin="python"

echo "[1/4] Applying database migrations..."
$python_bin manage.py migrate

echo "[2/4] Collecting static files..."
$python_bin manage.py collectstatic --no-input

echo "[3/4] Ensuring at least one superuser exists..."
if $python_bin - <<'PYCODE'
import sys
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured

try:
    User = get_user_model()
except ImproperlyConfigured:
    print("Django is not configured; activate your virtualenv first.")
    sys.exit(1)

if User.objects.filter(is_superuser=True).exists():
    sys.exit(0)

sys.exit(1)
PYCODE
then
  echo "Superuser already present; skipping creation."
else
  echo "No superuser detected; launching createsuperuser (Ctrl+C to skip)."
  $python_bin manage.py createsuperuser
fi

if [ -n "$ALGOLIA_APPLICATION_ID" ] && [ -n "$ALGOLIA_API_KEY" ]; then
  echo "[4/4] Initializing Algolia index (optional step)..."
  if $python_bin manage.py init_algolia_index; then
    echo "Algolia index initialized."
  else
    echo "Algolia initialization failed; continuing."
  fi
else
  echo "[4/4] Skipping Algolia init because credentials are missing."
fi

echo "Bootstrap complete. Reload the web app from the PythonAnywhere dashboard."
