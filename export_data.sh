#!/usr/bin/env bash
# Export data to fixtures for migration to production

echo "Exporting data to fixtures..."

# Create fixtures directory
mkdir -p fixtures

# Export users (excluding passwords for security)
python manage.py dumpdata users.User --indent 2 --exclude auth.permission --exclude contenttypes > fixtures/users.json

# Export dreams
python manage.py dumpdata dreams.Dream dreams.DreamTag --indent 2 > fixtures/dreams.json

# Export patterns
python manage.py dumpdata patterns --indent 2 > fixtures/patterns.json

# Export sharing data
python manage.py dumpdata sharing --indent 2 > fixtures/sharing.json

echo "Data export completed! Files saved in fixtures/"
echo ""
echo "To import in production:"
echo "1. python manage.py loaddata fixtures/users.json"
echo "2. python manage.py loaddata fixtures/dreams.json"
echo "3. python manage.py loaddata fixtures/patterns.json"
echo "4. python manage.py loaddata fixtures/sharing.json"