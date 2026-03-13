"""
One-time command to flag existing roll-on products in the database.
Usage: python manage.py mark_roll_ons
"""

from django.core.management.base import BaseCommand


ROLL_ON_NAMES = [
    "Rose Oud Roll On",
    "Musk Amber Roll On",
    "Sandalwood Mogra Roll On",
    "Black Musk Roll On",
]


class Command(BaseCommand):
    help = "Mark roll-on products with is_roll_on=True"

    def handle(self, *args, **options):
        from products.models import Product

        updated = Product.objects.filter(name__in=ROLL_ON_NAMES).update(is_roll_on=True)
        self.stdout.write(self.style.SUCCESS(f"[OK] Marked {updated} products as is_roll_on=True"))
