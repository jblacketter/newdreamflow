#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

# Initialize Algolia index (only if configured)
if [ ! -z "$ALGOLIA_APPLICATION_ID" ]; then
    echo "Initializing Algolia search index..."
    python manage.py init_algolia_index || echo "Algolia index initialization skipped"
fi

echo "Build completed successfully!"