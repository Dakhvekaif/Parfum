"""
One-time management command to re-assign existing products to their
correct collections. Run this on Render to fix the empty tester-box
endpoints:

    python manage.py fix_collections
"""

from django.core.management.base import BaseCommand


PRODUCT_COLLECTIONS = {
    "Alpine Noir EDP":         ["Swiss Products", "Best Sellers", "Tester Box 5", "Tester Box 10"],
    "Swiss Cedar & Vetiver":   ["Swiss Products", "New Arrivals", "Tester Box 10"],
    "Dark Oud Elixir":         ["Indian Products", "Wedding Collection", "Tester Box 5", "Tester Box 10"],
    "Aqua Sport Fresh":        ["Summer Essentials", "New Arrivals", "Tester Box 10"],
    "Midnight Rose Parfum":    ["Best Sellers", "Wedding Collection", "Tester Box 5", "Tester Box 10"],
    "Jasmine & White Tea":     ["Indian Products", "New Arrivals", "Tester Box 10"],
    "Velvet Orchid Luxe":      ["Swiss Products", "Best Sellers", "Tester Box 5", "Tester Box 10"],
    "Cherry Blossom Mist":     ["Summer Essentials", "New Arrivals", "Tester Box 10"],
    "Mysore Sandalwood Attar": ["Indian Products", "Best Sellers", "Wedding Collection", "Tester Box 10"],
    "Saffron & Amber Fusion":  ["Indian Products", "Wedding Collection"],
    "Citrus Bergamot Fresh":   ["Swiss Products", "Summer Essentials"],
    "Musk & Vanilla Unisex":   ["New Arrivals", "Best Sellers"],
}


class Command(BaseCommand):
    help = "Re-assign products to their correct collections (fixes empty tester-box endpoints)"

    def handle(self, *args, **options):
        from products.models import Collection, Product

        self.stdout.write("[FIX] Re-assigning product collections...")

        col_map = {c.name: c for c in Collection.objects.all()}
        missing_collections = []

        updated = 0
        for product_name, collection_names in PRODUCT_COLLECTIONS.items():
            try:
                product = Product.objects.get(name=product_name)
            except Product.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f"  [SKIP] Product not found: {product_name}")
                )
                continue

            for col_name in collection_names:
                col = col_map.get(col_name)
                if col:
                    product.collections.add(col)
                else:
                    if col_name not in missing_collections:
                        missing_collections.append(col_name)
                        # Create the missing collection
                        col, _ = Collection.objects.get_or_create(
                            name=col_name,
                            defaults={"description": f"{col_name} collection.", "is_active": True},
                        )
                        col_map[col_name] = col
                        self.stdout.write(f"  [CREATE] Created missing collection: {col_name}")
                    product.collections.add(col_map[col_name])

            updated += 1
            self.stdout.write(f"  [OK] {product_name} → {collection_names}")

        self.stdout.write(
            self.style.SUCCESS(f"[DONE] Updated collections for {updated} products.")
        )
