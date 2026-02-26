"""
Management command to populate the database with realistic perfume seed data.
Usage: python manage.py seed_data
       python manage.py seed_data --clear   (wipes existing data first)
"""

import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

User = get_user_model()


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
        from products.models import Category, Collection, Product, ProductImage
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
    # CATEGORIES
    # ------------------------------------------------------------------
    def _create_categories(self):
        from products.models import Category

        self.stdout.write("[CATEGORIES] Creating categories...")
        categories_data = [
            {"name": "Eau de Parfum", "description": "Long-lasting fragrances with 15-20% concentration. Perfect for all-day wear."},
            {"name": "Eau de Toilette", "description": "Light, refreshing scents with 5-15% concentration. Ideal for daily use."},
            {"name": "Body Mist", "description": "Ultra-light fragrance sprays for a subtle, refreshing scent throughout the day."},
            {"name": "Attar", "description": "Traditional oil-based perfumes, alcohol-free with rich, concentrated fragrance."},
            {"name": "Cologne", "description": "Classic light fragrances with 2-4% concentration. Fresh and invigorating."},
            {"name": "Gift Sets", "description": "Curated perfume gift boxes perfect for special occasions and celebrations."},
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
            {"name": "Summer Essentials", "description": "Light, citrusy fragrances perfect for hot Indian summers."},
            {"name": "Best Sellers", "description": "Our most popular perfumes loved by thousands of customers."},
            {"name": "Wedding Collection", "description": "Luxurious fragrances crafted for the most special day of your life."},
            {"name": "Office Wear", "description": "Subtle, sophisticated scents appropriate for professional settings."},
            {"name": "Date Night", "description": "Alluring, magnetic fragrances for romantic evenings."},
            {"name": "New Arrivals", "description": "The latest additions to our fragrance family."},
        ]

        collections = []
        for data in collections_data:
            col, _ = Collection.objects.get_or_create(name=data["name"], defaults=data)
            collections.append(col)

        self.stdout.write(f"  Created {len(collections)} collections")
        return collections

    # ------------------------------------------------------------------
    # PRODUCTS
    # ------------------------------------------------------------------
    def _create_products(self, categories, collections):
        from products.models import Product

        self.stdout.write("[PRODUCTS] Creating products...")

        products_data = [
            # Eau de Parfum
            {"name": "Swiss Aroma Noir Intense", "description": "A bold, mysterious blend of oud, black amber, and smoky vetiver. This intense fragrance commands attention and leaves a lasting impression.", "price": "2999.00", "discount_price": "2499.00", "stock": 50, "category": "Eau de Parfum", "collections": ["Best Sellers", "Date Night"]},
            {"name": "Royal Saffron Oud", "description": "An opulent fusion of precious saffron and rare oud wood. Enriched with rose absolute and golden amber for a truly regal experience.", "price": "4999.00", "discount_price": "4299.00", "stock": 30, "category": "Eau de Parfum", "collections": ["Wedding Collection", "Best Sellers"]},
            {"name": "Midnight Jasmine", "description": "Intoxicating night-blooming jasmine layered with white musk, sandalwood, and a hint of vanilla. Sensual and unforgettable.", "price": "3499.00", "stock": 45, "category": "Eau de Parfum", "collections": ["Date Night", "New Arrivals"]},
            {"name": "Velvet Rose & Amber", "description": "A romantic blend of Bulgarian rose, warm amber, and soft suede. Elegant and timeless for every occasion.", "price": "3299.00", "discount_price": "2799.00", "stock": 35, "category": "Eau de Parfum", "collections": ["Wedding Collection"]},
            {"name": "Alpine Fresh Pour Homme", "description": "Crisp mountain air meets bergamot, juniper berries, and cedarwood. A confident, modern masculine fragrance.", "price": "2799.00", "stock": 60, "category": "Eau de Parfum", "collections": ["Office Wear", "Best Sellers"]},

            # Eau de Toilette
            {"name": "Citrus Burst", "description": "An energizing splash of Italian lemon, grapefruit, and mandarin orange. Light, zesty, and perfect for Indian summers.", "price": "1499.00", "discount_price": "1199.00", "stock": 80, "category": "Eau de Toilette", "collections": ["Summer Essentials"]},
            {"name": "Ocean Breeze", "description": "Fresh marine notes blended with sea salt, driftwood, and white tea. Like a walk on a pristine Goan beach.", "price": "1699.00", "stock": 70, "category": "Eau de Toilette", "collections": ["Summer Essentials", "New Arrivals"]},
            {"name": "Green Tea & Bamboo", "description": "A serene, calming fragrance with green tea extract, fresh bamboo, and a touch of white iris.", "price": "1599.00", "discount_price": "1299.00", "stock": 55, "category": "Eau de Toilette", "collections": ["Office Wear"]},
            {"name": "Lavender Dreams", "description": "French lavender harmonized with tonka bean, coumarin, and creamy musk. Relaxing yet elegant.", "price": "1799.00", "stock": 40, "category": "Eau de Toilette", "collections": ["Office Wear", "New Arrivals"]},

            # Body Mist
            {"name": "Strawberry Kiss", "description": "A playful, fruity mist bursting with ripe strawberries, peach nectar, and cotton candy sweetness.", "price": "699.00", "discount_price": "549.00", "stock": 120, "category": "Body Mist", "collections": ["Summer Essentials", "Best Sellers"]},
            {"name": "Vanilla Cloud", "description": "Warm Madagascar vanilla wrapped in whipped cream and soft caramel. Cozy, comforting, and addictive.", "price": "749.00", "stock": 100, "category": "Body Mist", "collections": ["Best Sellers"]},
            {"name": "Tropical Paradise", "description": "Escape to the tropics with coconut water, pineapple, and frangipani flowers. Pure summer in a bottle.", "price": "649.00", "stock": 90, "category": "Body Mist", "collections": ["Summer Essentials"]},

            # Attar
            {"name": "Mysore Sandalwood Attar", "description": "Pure, authentic Mysore sandalwood oil. Warm, creamy, and meditative. A timeless Indian classic.", "price": "5999.00", "discount_price": "5499.00", "stock": 20, "category": "Attar", "collections": ["Wedding Collection", "Best Sellers"]},
            {"name": "Gulab Attar", "description": "Traditional rose attar distilled from thousands of Kannauj rose petals. Rich, deep, and absolutely natural.", "price": "3999.00", "stock": 25, "category": "Attar", "collections": ["Wedding Collection"]},
            {"name": "Musk Amber Attar", "description": "An exotic blend of white musk and golden amber. Oil-based, alcohol-free, and incredibly long-lasting.", "price": "2999.00", "stock": 30, "category": "Attar", "collections": ["Date Night"]},

            # Cologne
            {"name": "Classic Vetiver", "description": "Timeless vetiver cologne with hints of lemon and white pepper. The quintessential gentleman's fragrance.", "price": "999.00", "discount_price": "799.00", "stock": 75, "category": "Cologne", "collections": ["Office Wear"]},
            {"name": "Fresh Aqua Sport", "description": "An invigorating aquatic cologne designed for active lifestyles. Cool, clean, and energizing.", "price": "899.00", "stock": 85, "category": "Cologne", "collections": ["Summer Essentials"]},

            # Gift Sets
            {"name": "The Signature Collection Box", "description": "A luxury gift set featuring 5 of our bestselling miniatures (10ml each) in a premium wooden box. Perfect for gifting.", "price": "4499.00", "discount_price": "3799.00", "stock": 40, "category": "Gift Sets", "collections": ["Best Sellers", "Wedding Collection"]},
            {"name": "Date Night Duo", "description": "His & Hers fragrance set — Swiss Aroma Noir (50ml) + Midnight Jasmine (50ml) in a romantic gift box.", "price": "5499.00", "discount_price": "4799.00", "stock": 25, "category": "Gift Sets", "collections": ["Date Night", "New Arrivals"]},
        ]

        # Map category names to objects
        cat_map = {c.name: c for c in categories}
        col_map = {c.name: c for c in collections}

        products = []
        for data in products_data:
            cat_name = data.pop("collections_list", None) or data.pop("collections")
            category_name = data.pop("category")

            product, created = Product.objects.get_or_create(
                name=data["name"],
                defaults={
                    "description": data["description"],
                    "price": Decimal(data["price"]),
                    "discount_price": Decimal(data["discount_price"]) if data.get("discount_price") else None,
                    "stock": data["stock"],
                    "category": cat_map[category_name],
                    "is_active": True,
                },
            )

            if created:
                # Assign collections
                collection_names = cat_name if isinstance(cat_name, list) else [cat_name]
                for col_name in collection_names:
                    if col_name in col_map:
                        product.collections.add(col_map[col_name])

            products.append(product)

        self.stdout.write(f"  Created {len(products)} products")
        return products

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
            {"code": "FLAT500", "description": "Flat ₹500 off on orders above ₹2999", "discount_type": "fixed", "value": "500.00", "min_order_amount": "2999.00", "max_discount_amount": None, "valid_from": now - timedelta(days=5), "valid_until": now + timedelta(days=60), "usage_limit": 50},
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
    # ORDERS
    # ------------------------------------------------------------------
    def _create_orders(self, users, products):
        from orders.models import Order, OrderItem, Payment

        self.stdout.write("[ORDERS] Creating orders...")
        now = timezone.now()
        statuses = ["pending", "confirmed", "processing", "shipped", "delivered"]
        payment_methods = ["upi", "card", "cod", "wallet", "netbanking"]

        orders_created = 0
        for i, user in enumerate(users[:4]):  # First 4 users get orders
            num_orders = random.randint(1, 3)
            for j in range(num_orders):
                order_products = random.sample(products, random.randint(1, 4))
                subtotal = sum(p.effective_price * random.randint(1, 2) for p in order_products)
                status = random.choice(statuses)

                order = Order.objects.create(
                    user=user,
                    status=status,
                    subtotal=subtotal,
                    discount_amount=Decimal("0.00"),
                    total_amount=subtotal,
                    shipping_name=user.full_name,
                    shipping_address=user.address or "123 Test Street",
                    shipping_city=user.city or "Mumbai",
                    shipping_pincode=user.pincode or "400001",
                    shipping_phone=user.phone or "9876543210",
                )
                # Backdate some orders
                Order.objects.filter(pk=order.pk).update(
                    created_at=now - timedelta(days=random.randint(1, 60))
                )

                for product in order_products:
                    qty = random.randint(1, 2)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        quantity=qty,
                        price_at_purchase=product.effective_price,
                    )

                # Create payment
                pay_status = "completed" if status in ["confirmed", "processing", "shipped", "delivered"] else "pending"
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
                        "is_approved": random.choice([True, True, True, False]),  # 75% approved
                    },
                )
                if created:
                    reviews_created += 1

        self.stdout.write(f"  Created {reviews_created} reviews")

    # ------------------------------------------------------------------
    # CART & WISHLIST
    # ------------------------------------------------------------------
    def _create_cart_wishlist(self, users, products):
        from cart.models import Cart, CartItem, Wishlist

        self.stdout.write("[CART] Creating carts & wishlists...")

        for user in users[:3]:  # First 3 users get active carts
            cart, _ = Cart.objects.get_or_create(user=user)
            cart_products = random.sample(products, random.randint(1, 3))
            for product in cart_products:
                CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={"quantity": random.randint(1, 2)},
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
