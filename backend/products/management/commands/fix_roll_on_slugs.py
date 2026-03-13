"""Prints slugs for roll-on products."""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Print roll-on product slugs"

    def handle(self, *args, **options):
        from products.models import Product
        from django.utils.text import slugify

        rolls = Product.objects.filter(is_roll_on=True)
        for p in rolls:
            if not p.slug:
                p.slug = slugify(p.name)
                p.save(update_fields=["slug"])
                self.stdout.write(f"  Fixed slug: {p.name!r} → {p.slug!r}")
            else:
                self.stdout.write(f"  OK: {p.name!r} → slug={p.slug!r}")
