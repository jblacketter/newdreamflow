#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newdreamflow.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Check if admin user already exists
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',  # Change this password!
        # Additional fields for the custom User model
        theme='default',
    )
    print("Superuser created successfully!")
    print("Username: admin")
    print("Password: admin123")
    print("⚠️  Please change the password after logging in!")
else:
    print("Admin user already exists!")
