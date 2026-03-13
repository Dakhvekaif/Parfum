"""
Management command to populate the database with realistic perfume seed data.
Downloads product images from Unsplash so they persist across Render deploys.

Usage: python manage.py seed_data
       python manage.py seed_data --clear   (wipes existing data first)
"""

import random
import urllib.request
from datetime import timedelta
from decimal import Decimal
from io import BytesIO
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

User = get_user_model()

# ──────────────────────────────────────────────────
# UNSPLASH IMAGE URLS (free, permanent, high quality)
# Each product gets 2-3 unique images.
# ──────────────────────────────────────────────────
PRODUCT_IMAGES = {
    # ── Men's Fragrances ──
    "Alpine Noir EDP": [
        "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=800&q=80",
        "https://images.unsplash.com/photo-1541643600914-78b084683601?w=800&q=80",
        "https://images.unsplash.com/photo-1547887538-e3a2f32cb1cc?w=800&q=80",
    ],
    "Swiss Cedar & Vetiver": [
        "https://images.unsplash.com/photo-1587017539504-67cfbddac569?w=800&q=80",
        "https://images.unsplash.com/photo-1590736704728-f4730bb30770?w=800&q=80",
        "https://images.unsplash.com/photo-1595535373192-fc8935bacd89?w=800&q=80",
    ],
    "Dark Oud Elixir": [
        "https://images.unsplash.com/photo-1541643600914-78b084683601?w=800&q=80",
        "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=800&q=80",
        "https://images.unsplash.com/photo-1587017539504-67cfbddac569?w=800&q=80",
    ],
    "Aqua Sport Fresh": [
        "https://images.unsplash.com/photo-1557170334-a9632e77c6e4?w=800&q=80",
        "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=800&q=80",
    ],

    # ── Women's Fragrances ──
    "Midnight Rose Parfum": [
        "https://images.unsplash.com/photo-1588405748880-12d1d2a59f75?w=800&q=80",
        "https://images.unsplash.com/photo-1563170351-be82bc888aa4?w=800&q=80",
        "https://images.unsplash.com/photo-1541643600914-78b084683601?w=800&q=80",
    ],
    "Jasmine & White Tea": [
        "https://images.unsplash.com/photo-1557170334-a9632e77c6e4?w=800&q=80",
        "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=800&q=80",
        "https://images.unsplash.com/photo-1547887538-e3a2f32cb1cc?w=800&q=80",
    ],
    "Velvet Orchid Luxe": [
        "https://images.unsplash.com/photo-1592842232655-e5d345cbc2d0?w=800&q=80",
        "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=800&q=80",
    ],
    "Cherry Blossom Mist": [
        "https://images.unsplash.com/photo-1588405748880-12d1d2a59f75?w=800&q=80",
        "https://images.unsplash.com/photo-1563170351-be82bc888aa4?w=800&q=80",
        "https://images.unsplash.com/photo-1592842232655-e5d345cbc2d0?w=800&q=80",
    ],

    # ── Unisex Fragrances ──
    "Mysore Sandalwood Attar": [
        "https://images.unsplash.com/photo-1595535373192-fc8935bacd89?w=800&q=80",
        "https://images.unsplash.com/photo-1590736704728-f4730bb30770?w=800&q=80",
        "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=800&q=80",
    ],
    "Saffron & Amber Fusion": [
        "https://images.unsplash.com/photo-1547887538-e3a2f32cb1cc?w=800&q=80",
        "https://images.unsplash.com/photo-1541643600914-78b084683601?w=800&q=80",
    ],
    "Citrus Bergamot Fresh": [
        "https://images.unsplash.com/photo-1523293182086-7651a899d37f?w=800&q=80",
        "https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=800&q=80",
        "https://images.unsplash.com/photo-1557170334-a9632e77c6e4?w=800&q=80",
    ],
    "Musk & Vanilla Unisex": [
        "https://images.unsplash.com/photo-1587017539504-67cfbddac569?w=800&q=80",
        "https://images.unsplash.com/photo-1563170351-be82bc888aa4?w=800&q=80",
    ],

    # ── Roll On Attars ──
    "Rose Oud Roll On": [
        "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=800&q=80",
        "https://images.unsplash.com/photo-1563170351-be82bc888aa4?w=800&q=80",
    ],
    "Musk Amber Roll On": [
        "https://images.unsplash.com/photo-1595535373192-fc8935bacd89?w=800&q=80",
        "https://images.unsplash.com/photo-1547887538-e3a2f32cb1cc?w=800&q=80",
    ],
    "Sandalwood Mogra Roll On": [
        "https://images.unsplash.com/photo-1590736704728-f4730bb30770?w=800&q=80",
        "https://images.unsplash.com/photo-1592842232655-e5d345cbc2d0?w=800&q=80",
    ],
    "Black Musk Roll On": [
        "https://images.unsplash.com/photo-1541643600914-78b084683601?w=800&q=80",
        "https://images.unsplash.com/photo-1557170334-a9632e77c6e4?w=800&q=80",
    ],
}


class Command(BaseCommand):
    help = "Seed database with realistic perfume shop data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing seeded data before inserting",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_data()

        self.stdout.write(self.style.WARNING("[SEED] Seeding database..."))

        users = self._create_users()
        categories = self._create_categories()
        collections = self._create_collections()
        products = self._create_products(categories, collections)
        self._create_variants(products)
        self._create_product_images(products)
        self._create_discounts()
        self._create_orders(users, products)
        self._create_reviews(users, products)
        self._create_cart_wishlist(users, products)
        self._create_analytics()

        self.stdout.write(self.style.SUCCESS("[OK] Seed data created successfully!"))

    # ------------------------------------------------------------------
    # CLEAR
    # ------------------------------------------------------------------
    def _clear_data(self):
        from analytics.models import InventoryTransfer, SalesAnalytics
        from cart.models import Cart, CartItem, Wishlist
        from discounts.models import Discount
        from orders.models import Order, OrderItem, Payment
        from products.models import Category, Collection, Product, ProductImage, ProductVariant
        from reviews.models import Review

        self.stdout.write("[CLEAR] Clearing existing seed data...")
        Review.objects.all().delete()
        Payment.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Wishlist.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        InventoryTransfer.objects.all().delete()
        SalesAnalytics.objects.all().delete()
        Discount.objects.all().delete()
        ProductImage.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        Collection.objects.all().delete()
        Category.objects.all().delete()
        # Delete non-superuser, non-admin test users only
        User.objects.filter(is_superuser=False).exclude(email="test@example.com").delete()
        self.stdout.write(self.style.SUCCESS("  Cleared."))

    # ------------------------------------------------------------------
    # USERS
    # ------------------------------------------------------------------
    def _create_users(self):
        self.stdout.write("[USERS] Creating test users...")
        user_data = [
            {"email": "rahul.sharma@example.com", "first_name": "Rahul", "last_name": "Sharma", "phone": "9876543210", "address": "12 MG Road", "city": "Mumbai", "pincode": "400001"},
            {"email": "priya.patel@example.com", "first_name": "Priya", "last_name": "Patel", "phone": "9876543211", "address": "45 Brigade Road", "city": "Bangalore", "pincode": "560001"},
            {"email": "amit.kumar@example.com", "first_name": "Amit", "last_name": "Kumar", "phone": "9876543212", "address": "78 Connaught Place", "city": "Delhi", "pincode": "110001"},
            {"email": "sneha.reddy@example.com", "first_name": "Sneha", "last_name": "Reddy", "phone": "9876543213", "address": "23 Jubilee Hills", "city": "Hyderabad", "pincode": "500033"},
            {"email": "vikram.singh@example.com", "first_name": "Vikram", "last_name": "Singh", "phone": "9876543214", "address": "56 Civil Lines", "city": "Jaipur", "pincode": "302001"},
        ]

        users = []
        for data in user_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={**data, "role": "customer"},
            )
            if created:
                user.set_password("TestPass123!")
                user.save()
            users.append(user)

        self.stdout.write(f"  Created {len(users)} users")
        return users

    # ------------------------------------------------------------------
    # CATEGORIES (Men, Women, Unisex)
    # ------------------------------------------------------------------
    def _create_categories(self):
        from products.models import Category

        self.stdout.write("[CATEGORIES] Creating categories...")
        categories_data = [
            {"name": "Men", "description": "Bold, confident fragrances crafted for the modern man."},
            {"name": "Women", "description": "Elegant, captivating scents designed for her."},
            {"name": "Unisex", "description": "Versatile fragrances that transcend gender."},
        ]

        categories = []
        for data in categories_data:
            cat, _ = Category.objects.get_or_create(name=data["name"], defaults=data)
            categories.append(cat)

        self.stdout.write(f"  Created {len(categories)} categories")
        return categories

    # ------------------------------------------------------------------
    # COLLECTIONS
    # ------------------------------------------------------------------
    def _create_collections(self):
        from products.models import Collection

        self.stdout.write("[COLLECTIONS] Creating collections...")
        collections_data = [
            {"name": "Indian Products", "description": "Authentic Indian fragrances -- attars, sandalwood, and traditional scents."},
            {"name": "Swiss Products", "description": "Premium Swiss-crafted fragrances with Alpine-inspired ingredients."},
            {"name": "New Arrivals", "description": "The latest additions to our fragrance family."},
            {"name": "Best Sellers", "description": "Our most popular perfumes loved by thousands."},
            {"name": "Summer Essentials", "description": "Light, citrusy fragrances perfect for hot Indian summers."},
            {"name": "Wedding Collection", "description": "Luxurious fragrances for the most special day of your life."},
            {"name": "Tester Box 5", "description": "Try before you commit — 5 hand-picked testers in 5ml sample sizes."},
            {"name": "Tester Box 10", "description": "The ultimate sampler — 10 testers in 5ml sample sizes to explore our full range."},
        ]

        collections = []
        for data in collections_data:
            col, _ = Collection.objects.get_or_create(name=data["name"], defaults=data)
            collections.append(col)

        self.stdout.write(f"  Created {len(collections)} collections")
        return collections

    # ------------------------------------------------------------------
    # PRODUCTS (3-4 per category, no price/stock — that's in variants)
    # ------------------------------------------------------------------
    def _create_products(self, categories, collections):
        from products.models import Product

        self.stdout.write("[PRODUCTS] Creating products...")

        products_data = [
            # ── Men (4 products) ──
            {
                "name": "Alpine Noir EDP",
                "description": "A bold, mysterious blend of Swiss pine, black amber, and smoky vetiver. This intense Eau de Parfum commands attention with every step.",
                "category": "Men",
                "collections": ["Swiss Products", "Best Sellers", "Tester Box 5", "Tester Box 10"],
            },
            {
                "name": "Swiss Cedar & Vetiver",
                "description": "Crisp Alpine cedarwood meets earthy vetiver. Notes of bergamot and white pepper add a modern edge. Perfect for the office.",
                "category": "Men",
                "collections": ["Swiss Products", "New Arrivals", "Tester Box 10"],
            },
            {
                "name": "Dark Oud Elixir",
                "description": "A rich, opulent blend of aged Indian oud, saffron threads, and golden amber. Incredibly long-lasting.",
                "category": "Men",
                "collections": ["Indian Products", "Wedding Collection", "Tester Box 5", "Tester Box 10"],
            },
            {
                "name": "Aqua Sport Fresh",
                "description": "An invigorating aquatic cologne with sea salt, cucumber, and driftwood. Light enough for Indian summers.",
                "category": "Men",
                "collections": ["Summer Essentials", "New Arrivals", "Tester Box 10"],
            },

            # ── Women (4 products) ──
            {
                "name": "Midnight Rose Parfum",
                "description": "Intoxicating night-blooming Bulgarian rose layered with white musk, Turkish rose absolute, and warm vanilla base.",
                "category": "Women",
                "collections": ["Best Sellers", "Wedding Collection", "Tester Box 5", "Tester Box 10"],
            },
            {
                "name": "Jasmine & White Tea",
                "description": "Indian mogra jasmine with Japanese white tea and soft iris. Delicate yet long-lasting. Perfect for daytime wear.",
                "category": "Women",
                "collections": ["Indian Products", "New Arrivals", "Tester Box 10"],
            },
            {
                "name": "Velvet Orchid Luxe",
                "description": "An opulent floral-oriental masterpiece. Black orchid meets honey absolute, dark chocolate, and patchouli.",
                "category": "Women",
                "collections": ["Swiss Products", "Best Sellers", "Tester Box 5", "Tester Box 10"],
            },
            {
                "name": "Cherry Blossom Mist",
                "description": "A playful, light body mist with Japanese cherry blossom, peach nectar, and cotton candy sweetness.",
                "category": "Women",
                "collections": ["Summer Essentials", "New Arrivals", "Tester Box 10"],
            },

            # ── Unisex (4 products) ──
            {
                "name": "Mysore Sandalwood Attar",
                "description": "Pure, authentic Mysore sandalwood oil distilled using traditional Indian methods. Alcohol-free, 12+ hours.",
                "category": "Unisex",
                "collections": ["Indian Products", "Best Sellers", "Wedding Collection", "Tester Box 10"],
            },
            {
                "name": "Saffron & Amber Fusion",
                "description": "Kashmiri saffron meets golden amber with rose absolute and warm benzoin. A regal scent for special occasions.",
                "category": "Unisex",
                "collections": ["Indian Products", "Wedding Collection"],
            },
            {
                "name": "Citrus Bergamot Fresh",
                "description": "Italian bergamot, Sicilian lemon, and green mandarin balanced with white musk and light cedar.",
                "category": "Unisex",
                "collections": ["Swiss Products", "Summer Essentials"],
            },
            {
                "name": "Musk & Vanilla Unisex",
                "description": "A cozy, addictive blend of white musk, Madagascar vanilla, and soft sandalwood. Warm and inviting.",
                "category": "Unisex",
                "collections": ["New Arrivals", "Best Sellers"],
            },

            # ── Roll On Attars (4 products) ──
            {
                "name": "Rose Oud Roll On",
                "inspired_by": "Inspired by Rasasi's Dhan Al Oudh Abiyad",
                "description": "A rich, concentrated attar roll-on blending pure Bulgarian rose with aged Indian oud. Alcohol-free, long-lasting, and perfect for daily application directly on pulse points.",
                "is_roll_on": True,
                "category": "Unisex",
                "collections": ["Indian Products", "Best Sellers"],
            },
            {
                "name": "Musk Amber Roll On",
                "inspired_by": "Inspired by Swiss Arabian's Layali Rouge",
                "description": "Sensual white musk meets warm golden amber in this silky alcohol-free roll-on. Lingers beautifully on skin for hours. Ideal for travel.",
                "is_roll_on": True,
                "category": "Unisex",
                "collections": ["Indian Products", "New Arrivals"],
            },
            {
                "name": "Sandalwood Mogra Roll On",
                "inspired_by": "Inspired by Ajmal's Dahn Al Oudh Moattaq",
                "description": "Creamy Mysore sandalwood blended with fresh Indian mogra (jasmine). A classic attar combination in a convenient roll-on format. Zero alcohol, skin-safe.",
                "is_roll_on": True,
                "category": "Unisex",
                "collections": ["Indian Products", "Wedding Collection"],
            },
            {
                "name": "Black Musk Roll On",
                "inspired_by": "Inspired by Al Haramain's Black Musk",
                "description": "Deep, mysterious black musk attar with smoky oud undertones and a touch of vanilla. A crowd favourite — works on all skin types and lasts all day.",
                "is_roll_on": True,
                "category": "Unisex",
                "collections": ["Indian Products", "New Arrivals"],
            },
        ]

        cat_map = {c.name: c for c in categories}
        col_map = {c.name: c for c in collections}

        products = []
        for data in products_data:
            collection_names = data.pop("collections")
            category_name = data.pop("category")
            inspired_by = data.pop("inspired_by", "")
            is_roll_on = data.pop("is_roll_on", False)

            product, created = Product.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "inspired_by": inspired_by,
                    "is_roll_on": is_roll_on,
                    "category": cat_map[category_name],
                    "is_active": True,
                },
            )

            # Always sync collections (handles re-runs and manually-added products)
            for col_name in collection_names:
                if col_name in col_map:
                    product.collections.add(col_map[col_name])

            products.append(product)

        self.stdout.write(f"  Created {len(products)} products")
        return products

    # ------------------------------------------------------------------
    # VARIANTS — each product gets 10ml, 30ml, 50ml sizes
    # ------------------------------------------------------------------
    def _create_variants(self, products):
        from products.models import ProductVariant

        self.stdout.write("[VARIANTS] Creating product variants (10ml, 30ml, 50ml)...")

        # Price tiers: {product_name: {ml: (india_price, discount_price_or_None, switzerland_price)}}
        variant_prices = {
            "Alpine Noir EDP":         {5: ("249.00", None), 10: ("999.00", None), 30: ("2499.00", None), 50: ("3499.00", "2999.00")},
            "Swiss Cedar & Vetiver":   {5: ("199.00", None), 10: ("899.00", None), 30: ("2299.00", None), 50: ("2999.00", None)},
            "Dark Oud Elixir":         {5: ("349.00", None), 10: ("1499.00", None), 30: ("3999.00", None), 50: ("4999.00", "4499.00")},
            "Aqua Sport Fresh":        {5: ("99.00",  None), 10: ("499.00", None), 30: ("1199.00", "999.00"), 50: ("1499.00", "1199.00")},
            "Midnight Rose Parfum":    {5: ("299.00", None), 10: ("1199.00", None), 30: ("2999.00", None), 50: ("3999.00", "3499.00")},
            "Jasmine & White Tea":     {5: ("179.00", None), 10: ("799.00", None), 30: ("1999.00", None), 50: ("2499.00", None)},
            "Velvet Orchid Luxe":      {5: ("329.00", None), 10: ("1399.00", None), 30: ("3499.00", None), 50: ("4499.00", "3999.00")},
            "Cherry Blossom Mist":     {5: ("79.00",  None), 10: ("299.00", None), 30: ("699.00", "549.00"), 50: ("899.00", "699.00")},
            "Mysore Sandalwood Attar": {5: ("699.00", None), 10: ("2999.00", None), 30: ("5999.00", "5499.00"), 50: ("8999.00", None)},
            "Saffron & Amber Fusion":  {5: ("299.00", None), 10: ("1299.00", None), 30: ("2999.00", None), 50: ("3999.00", None)},
            "Citrus Bergamot Fresh":   {5: ("139.00", None), 10: ("599.00", None), 30: ("1499.00", None), 50: ("1999.00", "1699.00")},
            "Musk & Vanilla Unisex":   {5: ("159.00", None), 10: ("699.00", None), 30: ("1799.00", None), 50: ("2299.00", None)},
            # Roll On attars — always 10ml only
            "Rose Oud Roll On":         {10: ("499.00", "449.00")},
            "Musk Amber Roll On":       {10: ("399.00", "349.00")},
            "Sandalwood Mogra Roll On": {10: ("449.00", None)},
            "Black Musk Roll On":       {10: ("429.00", "379.00")},
        }

        stock_range = (20, 80)
        variants_created = 0

        for product in products:
            prices = variant_prices.get(product.name, {})
            for ml, (price, discount) in prices.items():
                _, created = ProductVariant.objects.get_or_create(
                    product=product,
                    quantity_ml=ml,
                    defaults={
                        "india_price": Decimal(price),
                        "india_discount_price": Decimal(discount) if discount else None,
                        "switzerland_price": Decimal(price) * Decimal('1.2'),
                        "india_stock": random.randint(*stock_range),
                        "switzerland_stock": random.randint(*stock_range),
                    },
                )
                if created:
                    variants_created += 1

        self.stdout.write(f"  Created {variants_created} variants")

    # ------------------------------------------------------------------
    # PRODUCT IMAGES — download from Unsplash
    # ------------------------------------------------------------------
    def _create_product_images(self, products):
        from products.models import ProductImage

        self.stdout.write("[IMAGES] Downloading product images from Unsplash...")
        images_created = 0

        for product in products:
            # Skip if product already has images
            if product.images.exists():
                continue

            urls = PRODUCT_IMAGES.get(product.name, [])
            if not urls:
                self.stdout.write(f"  [!] No images configured for: {product.name}")
                continue

            for sort_order, url in enumerate(urls):
                try:
                    req = urllib.request.Request(
                        url,
                        headers={"User-Agent": "SwissAroma-Seeder/1.0"},
                    )
                    response = urllib.request.urlopen(req, timeout=15)
                    image_data = response.read()

                    slug = product.slug or product.name.lower().replace(" ", "-")
                    filename = f"{slug}-{sort_order + 1}.jpg"

                    product_image = ProductImage(
                        product=product,
                        alt_text=f"{product.name} - Image {sort_order + 1}",
                        sort_order=sort_order,
                    )
                    product_image.image.save(
                        filename,
                        ContentFile(image_data),
                        save=True,
                    )
                    images_created += 1
                    self.stdout.write(f"  [OK] {product.name} -- image {sort_order + 1}")

                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f"  [FAIL] Failed to download image for {product.name}: {e}")
                    )

        self.stdout.write(f"  Downloaded {images_created} product images")

    # ------------------------------------------------------------------
    # DISCOUNTS
    # ------------------------------------------------------------------
    def _create_discounts(self):
        from discounts.models import Discount

        self.stdout.write("[DISCOUNTS] Creating discount codes...")
        now = timezone.now()

        discounts_data = [
            {"code": "WELCOME10", "description": "10% off on your first order", "discount_type": "percentage", "value": "10.00", "min_order_amount": "999.00", "max_discount_amount": "500.00", "valid_from": now - timedelta(days=30), "valid_until": now + timedelta(days=180), "usage_limit": 0},
            {"code": "SUMMER25", "description": "25% off on summer collection", "discount_type": "percentage", "value": "25.00", "min_order_amount": "1499.00", "max_discount_amount": "1000.00", "valid_from": now - timedelta(days=10), "valid_until": now + timedelta(days=90), "usage_limit": 100},
            {"code": "FLAT500", "description": "Flat Rs.500 off on orders above Rs.2999", "discount_type": "fixed", "value": "500.00", "min_order_amount": "2999.00", "max_discount_amount": None, "valid_from": now - timedelta(days=5), "valid_until": now + timedelta(days=60), "usage_limit": 50},
            {"code": "WEDDING15", "description": "15% off on wedding collection", "discount_type": "percentage", "value": "15.00", "min_order_amount": "3999.00", "max_discount_amount": "2000.00", "valid_from": now, "valid_until": now + timedelta(days=120), "usage_limit": 200},
            {"code": "EXPIRED20", "description": "This coupon has expired (for testing)", "discount_type": "percentage", "value": "20.00", "min_order_amount": "0.00", "max_discount_amount": None, "valid_from": now - timedelta(days=60), "valid_until": now - timedelta(days=1), "usage_limit": 0},
        ]

        for data in discounts_data:
            Discount.objects.get_or_create(
                code=data["code"],
                defaults={
                    "description": data["description"],
                    "discount_type": data["discount_type"],
                    "value": Decimal(data["value"]),
                    "min_order_amount": Decimal(data["min_order_amount"]),
                    "max_discount_amount": Decimal(data["max_discount_amount"]) if data["max_discount_amount"] else None,
                    "valid_from": data["valid_from"],
                    "valid_until": data["valid_until"],
                    "usage_limit": data["usage_limit"],
                    "is_active": True,
                },
            )

        self.stdout.write(f"  Created {len(discounts_data)} discount codes")

    # ------------------------------------------------------------------
    # ORDERS (now references variants)
    # ------------------------------------------------------------------
    def _create_orders(self, users, products):
        from orders.models import Order, OrderItem, Payment

        self.stdout.write("[ORDERS] Creating orders...")
        now = timezone.now()
        statuses = ["pending", "confirmed", "processing", "shipped", "delivered"]
        payment_methods = ["upi", "card", "cod", "wallet", "netbanking"]

        orders_created = 0
        for i, user in enumerate(users[:4]):
            num_orders = random.randint(1, 3)
            for j in range(num_orders):
                order_products = random.sample(products, random.randint(1, 4))
                # Pick a random variant for each product
                order_variants = []
                for p in order_products:
                    variant = p.variants.order_by("?").first()
                    if variant:
                        order_variants.append((p, variant))

                if not order_variants:
                    continue

                subtotal = sum(
                    v.india_effective_price * random.randint(1, 2)
                    for _, v in order_variants
                )
                order_status = random.choice(statuses)

                order = Order.objects.create(
                    user=user,
                    status=order_status,
                    subtotal=subtotal,
                    discount_amount=Decimal("0.00"),
                    total_amount=subtotal,
                    shipping_name=user.full_name,
                    shipping_address=user.address or "123 Test Street",
                    shipping_city=user.city or "Mumbai",
                    shipping_pincode=user.pincode or "400001",
                    shipping_phone=user.phone or "9876543210",
                )
                Order.objects.filter(pk=order.pk).update(
                    created_at=now - timedelta(days=random.randint(1, 60))
                )

                for product, variant in order_variants:
                    qty = random.randint(1, 2)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        variant=variant,
                        product_name=product.name,
                        quantity_ml=variant.quantity_ml,
                        selected_origin="india",
                        quantity=qty,
                        price_at_purchase=variant.india_effective_price,
                    )

                pay_status = "completed" if order_status in ["confirmed", "processing", "shipped", "delivered"] else "pending"
                Payment.objects.create(
                    order=order,
                    method=random.choice(payment_methods),
                    transaction_id=f"TXN{order.pk}{random.randint(100000, 999999)}",
                    amount=order.total_amount,
                    status=pay_status,
                    paid_at=now - timedelta(days=random.randint(1, 30)) if pay_status == "completed" else None,
                )

                orders_created += 1

        self.stdout.write(f"  Created {orders_created} orders with items & payments")

    # ------------------------------------------------------------------
    # REVIEWS
    # ------------------------------------------------------------------
    def _create_reviews(self, users, products):
        from django.db.models import Avg
        from reviews.models import Review

        self.stdout.write("[REVIEWS] Creating reviews...")
        review_comments = [
            "Absolutely love this fragrance! Long-lasting and gets me so many compliments.",
            "Good scent but doesn't last as long as I expected for the price.",
            "Best perfume I've ever bought. The packaging is also premium quality.",
            "Nice fragrance, perfect for office wear. Not too strong, just right.",
            "Gifted this to my wife and she loves it! Will buy more from this brand.",
            "Smells amazing for the first few hours, then fades a bit. Still worth it.",
            "The attar quality is exceptional. Genuine sandalwood, no synthetic smell.",
            "Received it well-packaged and on time. The scent is divine!",
            "A bit expensive but the quality justifies the price. 5 stars!",
            "Not my type of fragrance. Personal preference, quality is good though.",
        ]

        reviews_created = 0
        for user in users:
            reviewed_products = random.sample(products, min(random.randint(2, 5), len(products)))
            for product in reviewed_products:
                _, created = Review.objects.get_or_create(
                    user=user,
                    product=product,
                    defaults={
                        "rating": random.randint(3, 5),
                        "comment": random.choice(review_comments),
                        "is_approved": random.choice([True, True, True, False]),
                    },
                )
                if created:
                    reviews_created += 1

        # Recalculate avg_rating for all products based on approved reviews
        self.stdout.write("[REVIEWS] Recalculating product average ratings...")
        for product in products:
            avg = Review.objects.filter(
                product=product, is_approved=True
            ).aggregate(avg=Avg("rating"))["avg"]
            product.avg_rating = avg or 0
            product.save(update_fields=["avg_rating"])

        self.stdout.write(f"  Created {reviews_created} reviews")

    # ------------------------------------------------------------------
    # CART & WISHLIST (now uses variants)
    # ------------------------------------------------------------------
    def _create_cart_wishlist(self, users, products):
        from cart.models import Cart, CartItem, Wishlist

        self.stdout.write("[CART] Creating carts & wishlists...")

        for user in users[:3]:
            cart, _ = Cart.objects.get_or_create(user=user)
            cart_products = random.sample(products, random.randint(1, 3))
            for product in cart_products:
                variant = product.variants.order_by("?").first()
                if variant:
                    CartItem.objects.get_or_create(
                        cart=cart,
                        variant=variant,
                        defaults={"product": product, "quantity": random.randint(1, 2)},
                    )

        for user in users:
            wishlist_products = random.sample(products, random.randint(2, 5))
            for product in wishlist_products:
                Wishlist.objects.get_or_create(user=user, product=product)

        self.stdout.write("  Created carts & wishlists")

    # ------------------------------------------------------------------
    # ANALYTICS
    # ------------------------------------------------------------------
    def _create_analytics(self):
        from analytics.models import SalesAnalytics

        self.stdout.write("[ANALYTICS] Creating analytics data...")
        today = timezone.now().date()

        for i in range(30):
            date = today - timedelta(days=i)
            SalesAnalytics.objects.get_or_create(
                date=date,
                defaults={
                    "total_orders": random.randint(5, 30),
                    "total_revenue": Decimal(str(random.randint(15000, 120000))),
                    "products_sold": random.randint(10, 80),
                    "new_customers": random.randint(1, 10),
                },
            )

        self.stdout.write("  Created 30 days of analytics")
