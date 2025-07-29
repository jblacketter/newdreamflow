#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newdreamflow.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

try:
    admin = User.objects.get(username='admin')
    admin.set_password('admin123')  # Change this password!
    admin.save()
    print("Admin password reset successfully!")
    print("Username: admin")
    print("Password: admin123")
    print("⚠️  Please change the password after logging in!")
except User.DoesNotExist:
    print("Admin user not found!")