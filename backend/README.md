# Parfum Backend API

Django REST Framework backend for the Parfum e-commerce platform.

## Tech Stack

- **Django 5** + **Django REST Framework**
- **PostgreSQL** database
- **JWT Authentication** (SimpleJWT)
- **Argon2** password hashing

---

## Quick Setup (Local)

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

Copy the environment file and fill in your values:
```bash
cp .env.example .env
```

Run migrations and start the server:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data      # Populate with sample data
python manage.py runserver
```

API available at: **`http://127.0.0.1:8000/api/`**

> **For the deployed version:** `https://parfum-api.onrender.com/api/`

---

## How Auth Works

All protected endpoints need a **Bearer Token** in the header:
```
Authorization: Bearer <your_access_token>
```

You get tokens by **registering** or **logging in**. Access tokens expire in 1 day. Use the refresh token to get a new one.

---

## 🔓 Authentication Endpoints

### Register a New Account
```
POST /api/auth/register/
```
```json
{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "9876543210",
    "password": "SecurePass123!"
}
```
✅ Returns: `user` object + `tokens` (access + refresh)

### Login
```
POST /api/auth/login/
```
```json
{ "email": "user@example.com", "password": "SecurePass123!" }
```
✅ Returns: `user` object + `tokens`

### Logout
```
POST /api/auth/logout/
Authorization: Bearer <token>
```
```json
{ "refresh": "<refresh_token>" }
```

### Refresh Token (when access token expires)
```
POST /api/auth/token/refresh/
```
```json
{ "refresh": "<refresh_token>" }
```
✅ Returns: new `access` token

### Get / Update Profile
```
GET  /api/auth/profile/          # View your profile
PUT  /api/auth/profile/          # Update your profile
Authorization: Bearer <token>
```
Update body (all fields optional):
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "phone": "9876543210",
    "address": "123 Main St",
    "city": "Mumbai",
    "pincode": "400001"
}
```

### Change Password
```
POST /api/auth/change-password/
Authorization: Bearer <token>
```
```json
{ "old_password": "OldPass123!", "new_password": "NewPass456!" }
```

---

## 🛍️ Products (Public — No Auth Needed)

### List All Products
```
GET /api/products/
```

**Filters you can use:**

| Param | Example | What it does |
|-------|---------|-------------|
| `search` | `?search=jasmine` | Search name & description |
| `category__slug` | `?category__slug=attar` | Filter by category |
| `collection` | `?collection=best-sellers` | Filter by collection |
| `min_price` | `?min_price=1000` | Minimum price |
| `max_price` | `?max_price=5000` | Maximum price |
| `ordering` | `?ordering=-price` | Sort: `price`, `-price`, `name`, `-created_at`, `avg_rating` |
| `page` | `?page=2` | Pagination (20 per page) |

**Each product returns:**
```json
{
    "id": 1,
    "name": "Swiss Aroma Noir",
    "slug": "swiss-aroma-noir",
    "price": "2999.00",
    "discount_price": "2499.00",
    "effective_price": "2499.00",
    "discount_percentage": 17,
    "stock": 50,
    "quantity_ml": 100,
    "in_stock": true,
    "avg_rating": "4.50",
    "category": { "id": 1, "name": "Eau de Parfum", "slug": "eau-de-parfum" },
    "primary_image": "https://...",
    "created_at": "2026-01-15T10:00:00Z"
}
```

### Product Detail
```
GET /api/products/{slug}/
```
Returns full product with `images[]`, `collections[]`, `description`, `quantity_ml`

### Categories
```
GET /api/categories/
```
Returns all categories with `product_count`

### Collections
```
GET /api/collections/
```
Returns active collections with `product_count`

### Product Reviews
```
GET /api/products/{product_id}/reviews/
```
Returns approved reviews for a product

---

## 🛒 Cart (Auth Required)

### View Cart
```
GET /api/cart/
```
Returns: `items[]` with product details, `total_items`, `total_price`

### Add to Cart
```
POST /api/cart/add/
```
```json
{ "product_id": 1, "quantity": 1 }
```
> If product is already in cart, quantity gets incremented.

### Update Quantity
```
PUT /api/cart/update/{item_id}/
```
```json
{ "quantity": 3 }
```
> ⚠️ `item_id` = the **cart item ID** from the cart response, NOT the product ID!

### Remove Item
```
DELETE /api/cart/remove/{item_id}/
```

### Clear Entire Cart
```
DELETE /api/cart/clear/
```

---

## ❤️ Wishlist (Auth Required)

### View Wishlist
```
GET /api/wishlist/
```

### Toggle Add / Remove
```
POST /api/wishlist/toggle/
```
```json
{ "product_id": 1 }
```
- First call → **adds** to wishlist (`201`)
- Second call → **removes** from wishlist (`200`)

---

## 🏷️ Discounts (Auth Required)

### Apply / Validate Coupon
```
POST /api/discounts/apply/
```
```json
{ "code": "WELCOME10" }
```
✅ Returns: `discount_amount`, `cart_total`, `new_total`

> Cart must meet the coupon's minimum order amount.

---

## 📦 Orders (Auth Required)

### Checkout
```
POST /api/orders/checkout/
```
```json
{
    "shipping_name": "John Doe",
    "shipping_address": "123 Main Street",
    "shipping_city": "Mumbai",
    "shipping_pincode": "400001",
    "shipping_phone": "9876543210",
    "payment_method": "upi",
    "discount_code": "WELCOME10"
}
```
- `payment_method`: `upi`, `card`, `cod`, `wallet`, `netbanking`
- `discount_code`: optional
- Cart is cleared after successful checkout

### My Orders
```
GET /api/orders/
```

### Order Detail
```
GET /api/orders/{id}/
```
Includes `items[]` and `payment` info

### Record Payment
```
POST /api/orders/{order_id}/payment/
```
```json
{ "transaction_id": "UPI123456789", "method": "upi" }
```

---

## ⭐ Reviews (Auth Required)

### Submit a Review
```
POST /api/reviews/
```
```json
{ "product": 1, "rating": 5, "comment": "Amazing fragrance!" }
```
- Rating: **1–5**
- One review per user per product
- Reviews need admin approval before showing publicly

---

## 🔐 Admin Endpoints (Admin Only)

> All admin endpoints require a JWT from a user with `role = "admin"` or `is_superuser = True`.

### Dashboard Stats
```
GET /api/admin/analytics/dashboard/
```
Returns: `total_revenue`, `total_orders`, `total_customers`, `total_products`, `pending_orders`, `low_stock_products`, `recent_orders[]`, `revenue_trend[]`

### Sales Analytics
```
GET /api/admin/analytics/sales/
GET /api/admin/analytics/sales/?start_date=2026-01-01&end_date=2026-02-28
```

---

### 👥 Customers List
```
GET /api/admin/customers/
```

**Filters:**

| Param | Example | What it does |
|-------|---------|-------------|
| `search` | `?search=john` | Search by name, email, phone, city |
| `ordering` | `?ordering=-total_spent` | Sort: `date_joined`, `first_name`, `orders_count`, `total_spent` |

**Each customer returns:**
```json
{
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "9876543210",
    "city": "Mumbai",
    "date_joined": "2026-01-15T00:00:00Z",
    "orders_count": 3,
    "total_spent": "4500.00",
    "last_order_date": "2026-03-10T12:30:00Z",
    "is_active": true
}
```

---

### 📦 Products CRUD
```
GET    /api/admin/products/              # List all
POST   /api/admin/products/              # Create
GET    /api/admin/products/{id}/         # Detail
PATCH  /api/admin/products/{id}/         # Update
DELETE /api/admin/products/{id}/         # Delete
```

Create / Update body:
```json
{
    "name": "New Perfume",
    "description": "Description here",
    "price": "1999.00",
    "discount_price": "1499.00",
    "stock": 50,
    "quantity_ml": 100,
    "category_id": 1,
    "collection_ids": [1, 2],
    "is_active": true
}
```

> ⚠️ **Delete note:** If the product has existing orders, it **can't** be deleted (returns 400). Deactivate it instead by setting `"is_active": false`.

### 🖼️ Product Image Upload
```
POST   /api/admin/products/{product_id}/images/       # Upload image
DELETE /api/admin/products/{product_id}/images/?image_id=1   # Delete image
```
**Upload as `multipart/form-data`**, NOT JSON:
- `image`: the image file
- `alt_text`: description (string, optional)
- `is_primary`: `true` or `false` (optional — first image is auto-set as primary)

---

### 📁 Categories CRUD
```
GET    /api/admin/categories/
POST   /api/admin/categories/
PATCH  /api/admin/categories/{id}/
DELETE /api/admin/categories/{id}/
```
```json
{ "name": "Deodorants", "description": "Long-lasting sprays" }
```

### 📁 Collections CRUD
```
GET    /api/admin/collections/
POST   /api/admin/collections/
PATCH  /api/admin/collections/{id}/
DELETE /api/admin/collections/{id}/
```
```json
{ "name": "Monsoon Specials", "description": "Fresh scents", "is_active": true }
```

---

### 📋 Orders Management
```
GET /api/admin/orders/                   # All orders
PUT /api/admin/orders/{id}/status/       # Update status
```
```json
{ "status": "shipped", "tracking_id": "TRACK123", "notes": "Via BlueDart" }
```
Status options: `pending`, `confirmed`, `processing`, `shipped`, `delivered`, `cancelled`, `refunded`

### ✅ Reviews Management
```
GET /api/admin/reviews/                  # All reviews
GET /api/admin/reviews/?approved=false   # Pending only
PUT /api/admin/reviews/{id}/approve/     # Approve or reject
```
```json
{ "approve": true }
```

### 🏷️ Discounts CRUD
```
GET    /api/admin/discounts/
POST   /api/admin/discounts/
PATCH  /api/admin/discounts/{id}/
DELETE /api/admin/discounts/{id}/
```
```json
{
    "code": "MONSOON30",
    "description": "30% off",
    "discount_type": "percentage",
    "value": "30.00",
    "min_order_amount": "1500.00",
    "max_discount_amount": "1000.00",
    "valid_from": "2026-01-01T00:00:00Z",
    "valid_until": "2026-12-31T23:59:59Z",
    "usage_limit": 100,
    "is_active": true
}
```
`discount_type`: `percentage` or `fixed`

### 📊 Inventory Transfers
```
POST /api/admin/inventory/transfer/      # Record stock in/out
GET  /api/admin/inventory/transfers/     # Transfer history
GET  /api/admin/inventory/transfers/?product_id=1
```
```json
{ "product_id": 1, "transfer_type": "in", "quantity": 25, "notes": "New stock" }
```
`transfer_type`: `in` or `out`

---

## ⚠️ Error Codes

| Code | What it means |
|------|--------------|
| `400` | Bad request — check your JSON body |
| `401` | Not logged in or token expired — login again |
| `403` | You don't have permission (not admin) |
| `404` | Not found |
| `429` | Too many requests — slow down |

## ⏱️ Rate Limits

| Who | Limit |
|-----|-------|
| Not logged in | 30 requests/minute |
| Logged in | 100 requests/minute |
| Auth endpoints (login/register) | 5 requests/minute |

---

## 🚀 Deploy to Render (Free Tier)

### 1. Create PostgreSQL Database
- [Render Dashboard](https://dashboard.render.com/) → **New +** → **PostgreSQL**
- Name: `parfum-db` → Plan: **Free** → Create
- Copy the **Internal Database URL**

### 2. Create Web Service
- **New +** → **Web Service** → Connect GitHub repo (`Dakhvekaif/Parfum`)
- **Root Directory**: `backend`
- **Runtime**: Python
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn parfum.wsgi:application`
- **Plan**: Free

### 3. Set Environment Variables

| Key | Value |
|-----|-------|
| `SECRET_KEY` | *(generate a random one)* |
| `DEBUG` | `False` |
| `RENDER` | `True` |
| `DATABASE_URL` | *(Internal Database URL from step 1)* |
| `ALLOWED_HOSTS` | `parfum-api.onrender.com` |
| `DJANGO_SUPERUSER_EMAIL` | `admin@parfum.com` |
| `DJANGO_SUPERUSER_PASSWORD` | *(your admin password)* |
| `PYTHON_VERSION` | `3.13.2` |

### 4. Deploy
Click **Create Web Service**. Render auto-runs `build.sh` which:
- Installs dependencies
- Collects static files
- Runs migrations
- Creates the superuser
- Seeds sample data

> ⏳ Free tier sleeps after 15 min idle. First request after sleep takes ~30-50 seconds.

**API will be live at:** `https://parfum-api.onrender.com/api/`
