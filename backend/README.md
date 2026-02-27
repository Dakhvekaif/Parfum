# Parfum Backend API

Django REST Framework backend for the Parfum e-commerce platform.

## Tech Stack

- **Django 5** + **Django REST Framework**
- **PostgreSQL** database
- **JWT Authentication** (SimpleJWT)
- **Argon2** password hashing

## Quick Setup

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

API available at `http://127.0.0.1:8000/api/`

---

## Authentication

All protected endpoints use **Bearer Token** authentication.

### Register
```
POST /api/auth/register/
```
```json
{
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "9876543210",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
}
```
**Response:** `201` — returns `user` object + `tokens` (`access`, `refresh`)

### Login
```
POST /api/auth/login/
```
```json
{ "email": "user@example.com", "password": "SecurePass123!" }
```
**Response:** `200` — returns `user` + `tokens`

### Logout
```
POST /api/auth/logout/
Authorization: Bearer <access_token>
```
```json
{ "refresh": "<refresh_token>" }
```

### Refresh Token
```
POST /api/auth/token/refresh/
```
```json
{ "refresh": "<refresh_token>" }
```
**Response:** `200` — new `access` token

### Profile (GET / PUT)
```
GET  /api/auth/profile/
PUT  /api/auth/profile/
Authorization: Bearer <access_token>
```
PUT body (all optional):
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
Authorization: Bearer <access_token>
```
```json
{ "old_password": "OldPass123!", "new_password": "NewPass456!" }
```

---

## Products (Public — No Auth Required)

### List Products
```
GET /api/products/
```
**Query Parameters:**

| Param | Example | Description |
|-------|---------|-------------|
| `search` | `?search=jasmine` | Search name & description |
| `category__slug` | `?category__slug=attar` | Filter by category |
| `collection` | `?collection=best-sellers` | Filter by collection slug |
| `min_price` | `?min_price=1000` | Minimum price |
| `max_price` | `?max_price=5000` | Maximum price |
| `ordering` | `?ordering=price` | Sort by: `price`, `-price`, `name`, `-created_at`, `avg_rating` |
| `page` | `?page=2` | Pagination (20 per page) |

**Response:** Paginated list with `count`, `next`, `previous`, `results`

Each product includes: `id`, `name`, `slug`, `price`, `discount_price`, `effective_price`, `discount_percentage`, `stock`, `quantity_ml`, `in_stock`, `avg_rating`, `category` (nested), `primary_image`

### Product Detail
```
GET /api/products/{slug}/
```
Returns full product with `images[]`, `collections[]`, `description`

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

## Cart (Auth Required)

### View Cart
```
GET /api/cart/
```
**Response:** `items[]` with product details, `total_items`, `total_price`

### Add to Cart
```
POST /api/cart/add/
```
```json
{ "product_id": 1, "quantity": 1 }
```
Adds product or increments quantity if already in cart.

### Update Quantity
```
PUT /api/cart/update/{item_id}/
```
```json
{ "quantity": 3 }
```
`item_id` = the cart item ID (from cart response), not product ID.

### Remove Item
```
DELETE /api/cart/remove/{item_id}/
```

### Clear Cart
```
DELETE /api/cart/clear/
```

---

## Wishlist (Auth Required)

### View Wishlist
```
GET /api/wishlist/
```

### Toggle (Add/Remove)
```
POST /api/wishlist/toggle/
```
```json
{ "product_id": 1 }
```
- First call → adds to wishlist (`201`)
- Second call → removes from wishlist (`200`)

---

## Discounts (Auth Required)

### Apply / Validate Coupon
```
POST /api/discounts/apply/
```
```json
{ "code": "WELCOME10" }
```
**Response:** `discount_amount`, `cart_total`, `new_total`

> Validates against current cart total. Cart must meet minimum order amount.

---

## Orders (Auth Required)

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
`payment_method` options: `upi`, `card`, `cod`, `wallet`, `netbanking`

`discount_code` is optional. Cart is cleared after successful checkout.

### My Orders
```
GET /api/orders/
```

### Order Detail
```
GET /api/orders/{id}/
```
Includes `items[]` and `payment` info.

### Record Payment
```
POST /api/orders/{order_id}/payment/
```
```json
{ "transaction_id": "UPI123456789", "method": "upi" }
```

---

## Reviews (Auth Required)

### Submit Review
```
POST /api/reviews/
```
```json
{ "product": 1, "rating": 5, "comment": "Amazing fragrance!" }
```
Rating: 1–5. One review per user per product. Pending admin approval.

---

## Admin Endpoints (Admin Auth Required)

All admin endpoints require a user with `role = "admin"` or `is_superuser = True`.

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

### Products CRUD
```
GET    /api/admin/products/              # List all
POST   /api/admin/products/              # Create
GET    /api/admin/products/{id}/         # Detail
PATCH  /api/admin/products/{id}/         # Update
DELETE /api/admin/products/{id}/         # Delete
```
Create/Update body:
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

### Categories CRUD
```
GET    /api/admin/categories/
POST   /api/admin/categories/
PATCH  /api/admin/categories/{id}/
DELETE /api/admin/categories/{id}/
```
```json
{ "name": "Deodorants", "description": "Long-lasting sprays" }
```

### Collections CRUD
```
GET    /api/admin/collections/
POST   /api/admin/collections/
PATCH  /api/admin/collections/{id}/
DELETE /api/admin/collections/{id}/
```
```json
{ "name": "Monsoon Specials", "description": "Fresh scents", "is_active": true }
```

### Orders Management
```
GET /api/admin/orders/                   # All orders
PUT /api/admin/orders/{id}/status/       # Update status
```
```json
{ "status": "shipped", "tracking_id": "TRACK123", "notes": "Via BlueDart" }
```
Status options: `pending`, `confirmed`, `processing`, `shipped`, `delivered`, `cancelled`, `refunded`

### Reviews Management
```
GET /api/admin/reviews/                  # All reviews
GET /api/admin/reviews/?approved=false   # Pending only
PUT /api/admin/reviews/{id}/approve/     # Approve/reject
```
```json
{ "approve": true }    // or false to delete
```

### Discounts CRUD
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

### Inventory Transfers
```
POST /api/admin/inventory/transfer/      # Record stock in/out
GET  /api/admin/inventory/transfers/     # History
GET  /api/admin/inventory/transfers/?product_id=1
```
```json
{ "product_id": 1, "transfer_type": "in", "quantity": 25, "notes": "New stock" }
```
`transfer_type`: `in` or `out`

### Product Image Upload
```
POST   /api/admin/products/{product_id}/images/    # Upload (multipart/form-data)
DELETE /api/admin/products/{product_id}/images/?image_id=1
```
Form fields: `image` (file), `alt_text` (string), `is_primary` (true/false)

---

## Error Responses

| Code | Meaning |
|------|---------|
| `400` | Validation error — check request body |
| `401` | Token missing/invalid/expired — login again |
| `403` | Not authorized (wrong role) |
| `404` | Resource not found |
| `429` | Rate limited — wait and retry |

## Rate Limits

| User Type | Limit |
|-----------|-------|
| Anonymous | 30 requests/minute |
| Authenticated | 100 requests/minute |
| Auth endpoints | 5 requests/minute |

---

## Deploy to Render (Free Tier)

### 1. Create PostgreSQL Database
- Go to [Render Dashboard](https://dashboard.render.com/) → **New** → **PostgreSQL**
- Name: `parfum-db`
- Plan: **Free**
- Copy the **Internal Database URL** after creation

### 2. Create Web Service
- **New** → **Web Service** → Connect your GitHub repo
- **Root Directory**: `backend`
- **Runtime**: Python
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn parfum.wsgi:application`

### 3. Set Environment Variables
In the web service settings, add:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | Generate one: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `False` |
| `RENDER` | `True` |
| `DATABASE_URL` | *(paste Internal Database URL from step 1)* |
| `ALLOWED_HOSTS` | `your-app-name.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | `https://your-frontend-url.com` |

### 4. Deploy
Render will automatically run `build.sh` and start the server.

**Create superuser** via Render Shell tab:
```bash
python manage.py createsuperuser
```

**Seed data** (optional):
```bash
python manage.py seed_data
```

> **Note:** Free tier spins down after 15 min of inactivity. First request after idle takes ~30-50 seconds.

API will be live at: `https://your-app-name.onrender.com/api/`

