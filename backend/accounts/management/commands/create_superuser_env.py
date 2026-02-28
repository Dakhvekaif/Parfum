"""
Management command to create a superuser from environment variables.
Used on Render (free tier has no shell access).
Usage: python manage.py create_superuser_env
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create superuser from DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD env vars"

    def handle(self, *args, **options):
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not email or not password:
            self.stdout.write(self.style.WARNING(
                "Skipping superuser creation — DJANGO_SUPERUSER_EMAIL or DJANGO_SUPERUSER_PASSWORD not set."
            ))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.SUCCESS(f"Superuser '{email}' already exists — skipping."))
            return

        User.objects.create_superuser(email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f"Superuser '{email}' created successfully!"))
