# Parfum API Quick Reference

**Base URL:** `https://parfum-api.onrender.com/api/`  
**Auth Header:** `Authorization: Bearer <access_token>` (where noted 🔒)

---

## 🔐 AUTH

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
  "password": "SecurePass123!"
}
```
**Response:** user object + `tokens` → `{ "access": "...", "refresh": "..." }`

---

### Login
```
POST /api/auth/login/
```
```json
{ "email": "user@example.com", "password": "SecurePass123!" }
```
**Response:** user object + `tokens` → `{ "access": "...", "refresh": "..." }`

---

### Logout 🔒
```
POST /api/auth/logout/
```
```json
{ "refresh": "<refresh_token>" }
```

---

### Refresh Token
```
POST /api/auth/token/refresh/
```
```json
{ "refresh": "<refresh_token>" }
```
**Response:** `{ "access": "<new_access_token>" }`

---

### Get Profile 🔒
```
GET /api/auth/profile/
```
**Response:** `{ "email", "first_name", "last_name", "phone", "address", "city", "pincode" }`

---

### Update Profile 🔒
```
PATCH /api/auth/profile/
```
```json
{ "first_name": "Jane", "phone": "9999999999", "city": "Mumbai" }
```

---

### Change Password 🔒
```
POST /api/auth/change-password/
```
```json
{ "old_password": "OldPass123!", "new_password": "NewPass456!" }
```

---
---

## 🛍️ PRODUCTS (No auth needed)

### Product List
```
GET /api/products/
```
**Filters (query params):**
| Param | Example | What it does |
|-------|---------|--------------|
| `category__slug` | `?category__slug=men` | Filter by category |
| `collection` | `?collection=best-sellers` | Filter by collection |
| `search` | `?search=rose` | Search name & description |
| `min_price` | `?min_price=1000` | Min variant price |
| `max_price` | `?max_price=3000` | Max variant price |
| `ordering` | `?ordering=name` | Sort: `name`, `-created_at`, `avg_rating` |
| `page` | `?page=2` | Pagination (20/page) |

**Response (each product):**
```json
{
  "id": 1,
  "name": "Alpine Noir EDP",
  "slug": "alpine-noir-edp",
  "starting_price": "999.00",
  "in_stock": true,
  "avg_rating": "4.50",
  "category": { "id": 1, "name": "Men", "slug": "men" },
  "primary_image": { "id": 1, "image": "https://...", "alt_text": "...", "sort_order": 0 },
  "variants": [
    { "id": 1, "quantity_ml": 10, "price": "999.00", "discount_price": null, "effective_price": "999.00", "discount_percentage": 0, "stock": 40, "in_stock": true },
    { "id": 2, "quantity_ml": 30, "price": "2499.00", "discount_price": null, "effective_price": "2499.00", "discount_percentage": 0, "stock": 25, "in_stock": true },
    { "id": 3, "quantity_ml": 50, "price": "3499.00", "discount_price": "2999.00", "effective_price": "2999.00", "discount_percentage": 14, "stock": 15, "in_stock": true }
  ],
  "created_at": "2026-01-15T10:00:00Z"
}
```

---

### Product Detail
```
GET /api/products/{slug}/
```
**Response:** Same as above + `description`, `images[]`, `collections[]`

---

### Categories
```
GET /api/categories/
```
**Response:**
```json
[
  { "id": 1, "name": "Men", "slug": "men", "description": "...", "image": null, "product_count": 4 },
  { "id": 2, "name": "Women", "slug": "women", "description": "...", "image": null, "product_count": 4 },
  { "id": 3, "name": "Unisex", "slug": "unisex", "description": "...", "image": null, "product_count": 4 }
]
```

---

### Collections
```
GET /api/collections/
```
**Response:**
```json
[
  { "id": 1, "name": "Indian Products", "slug": "indian-products", "product_count": 4 },
  { "id": 2, "name": "Swiss Products", "slug": "swiss-products", "product_count": 4 },
  { "id": 3, "name": "New Arrivals", "slug": "new-arrivals", "product_count": 4 }
]
```

---

### Product Reviews
```
GET /api/products/{product_id}/reviews/
```
**Response:**
```json
[
  { "id": 1, "user": "rahul.sharma@example.com", "rating": 5, "comment": "Amazing!", "created_at": "..." }
]
```

---
---

## 🛒 CART 🔒 (All need auth token)

### View Cart
```
GET /api/cart/
```
**Response:**
```json
{
  "id": 1,
  "items": [
    {
      "id": 7,
      "product": { "id": 1, "name": "Alpine Noir EDP", "slug": "alpine-noir-edp", "..." },
      "variant": { "id": 3, "quantity_ml": 50, "price": "3499.00", "discount_price": "2999.00", "effective_price": "2999.00", "stock": 15 },
      "quantity": 1,
      "line_total": "2999.00"
    }
  ],
  "total_items": 1,
  "total_price": "2999.00"
}
```

---

### Add to Cart
```
POST /api/cart/add/
```
```json
{ "variant_id": 3, "quantity": 1 }
```
> ⚠️ Uses `variant_id` (the specific ML size ID), NOT `product_id`!  
> If same variant already in cart → quantity gets incremented.

**Response:** Full cart object (same as View Cart)

---

### Update Quantity
```
PUT /api/cart/update/{item_id}/
```
```json
{ "quantity": 3 }
```
> `item_id` = the **cart item ID** from the cart response (field `"id": 7` inside `items[]`), NOT the variant or product ID!

**Response:** Full cart object

---

### Remove Item
```
DELETE /api/cart/remove/{item_id}/
```
**Response:** Full cart object (without the removed item)

---

### Clear Entire Cart
```
DELETE /api/cart/clear/
```
**Response:** Empty cart object

---
---

## ❤️ WISHLIST 🔒

### View Wishlist
```
GET /api/wishlist/
```
**Response:**
```json
[
  { "id": 1, "product": { "id": 1, "name": "Alpine Noir EDP", "..." }, "created_at": "..." }
]
```

---

### Toggle Wishlist (Add/Remove)
```
POST /api/wishlist/toggle/
```
```json
{ "product_id": 1 }
```
> Wishlist uses `product_id` (not variant_id — you wishlist the product, not a size).  
> Call once → adds. Call again → removes.

**Response:** `{ "message": "Added to wishlist.", "wishlisted": true }` or `{ "message": "Removed from wishlist.", "wishlisted": false }`

---
---

## 📦 ORDERS 🔒

### Checkout (Cart → Order)
```
POST /api/orders/checkout/
```
```json
{
  "shipping_name": "Rahul Sharma",
  "shipping_address": "12 MG Road, Bandra West",
  "shipping_city": "Mumbai",
  "shipping_pincode": "400001",
  "shipping_phone": "9876543210",
  "payment_method": "upi",
  "discount_code": "WELCOME10"
}
```
> `payment_method` options: `upi`, `card`, `cod`, `wallet`, `netbanking`  
> `discount_code` is optional — leave blank or omit if no coupon.

**Response:** Full order object with `items[]`, `payment`, totals.

---

### Order History
```
GET /api/orders/
```
**Response:**
```json
[
  { "id": 1, "order_number": "ORD-0001", "status": "delivered", "status_display": "Delivered", "total_amount": "2999.00", "item_count": 2, "created_at": "..." }
]
```

---

### Order Detail
```
GET /api/orders/{id}/
```
**Response:** Full order with `items[]` (each has `product_name`, `quantity_ml`, `quantity`, `price_at_purchase`, `line_total`) + `payment` info.

---

### Record Payment
```
POST /api/orders/{order_id}/payment/
```
```json
{ "transaction_id": "UPI123456789", "method": "upi" }
```

---
---

## ⭐ REVIEWS 🔒

### Submit Review
```
POST /api/reviews/
```
```json
{ "product": 1, "rating": 5, "comment": "Amazing fragrance!" }
```
> Rating: 1–5. One review per user per product.

---
---

## 🏷️ DISCOUNTS

### Apply Discount (check if valid) 🔒
```
POST /api/discounts/apply/
```
```json
{ "code": "WELCOME10" }
```
**Response:** `{ "valid": true, "discount_type": "percentage", "value": "10.00", "message": "..." }`

---
---

## 🔑 TEST ACCOUNTS

| Email | Password | Role |
|-------|----------|------|
| `admin@parfum.com` | *(env var)* | Admin |
| `rahul.sharma@example.com` | `TestPass123!` | Customer |
| `priya.patel@example.com` | `TestPass123!` | Customer |
| `amit.kumar@example.com` | `TestPass123!` | Customer |

---

## 📊 ADMIN ENDPOINTS 🔒 (Admin only)

These need admin auth token.

| Method | Endpoint | Body / Notes |
|--------|----------|-------------|
| `GET` | `/api/admin/products/` | List all products |
| `POST` | `/api/admin/products/` | `{ "name", "description", "category_id", "collection_ids", "is_active" }` |
| `GET` | `/api/admin/products/{id}/` | Product detail |
| `PATCH` | `/api/admin/products/{id}/` | Update fields |
| `DELETE` | `/api/admin/products/{id}/` | Delete (fails if has orders) |
| `POST` | `/api/admin/products/{id}/variants/` | `{ "quantity_ml": 50, "price": "2999.00", "discount_price": null, "stock": 30 }` |
| `PUT` | `/api/admin/products/{id}/variants/{vid}/` | Update variant price/stock |
| `DELETE` | `/api/admin/products/{id}/variants/{vid}/` | Remove a size variant |
| `POST` | `/api/admin/products/{id}/images/` | Upload: `multipart/form-data` → `image` file + `alt_text` |
| `DELETE` | `/api/admin/products/{id}/images/?image_id=1` | Delete image |
| `GET/POST/PATCH/DELETE` | `/api/admin/categories/` | CRUD categories |
| `GET/POST/PATCH/DELETE` | `/api/admin/collections/` | CRUD collections |
| `GET` | `/api/admin/orders/` | All orders (`?status=pending` filter) |
| `PUT` | `/api/admin/orders/{id}/status/` | `{ "status": "shipped", "tracking_id": "...", "notes": "..." }` |
| `GET` | `/api/admin/customers/` | All customers with order stats |
| `GET` | `/api/admin/reviews/` | All reviews |
| `PUT` | `/api/admin/reviews/{id}/approve/` | `{ "is_approved": true }` |
| `GET` | `/api/admin/analytics/dashboard/` | Dashboard stats |
| `GET` | `/api/admin/analytics/sales/` | Sales data (`?start_date=`, `?end_date=`) |
| `POST` | `/api/admin/inventory/transfer/` | `{ "product_id": 1, "variant_id": 3, "transfer_type": "in", "quantity": 25 }` |
| `GET` | `/api/admin/inventory/transfers/` | Transfer history |

**Order status options:** `pending`, `confirmed`, `processing`, `shipped`, `delivered`, `cancelled`

---

## ⚠️ COMMON ERRORS

| Code | What it means |
|------|--------------|
| `400` | Bad request — check your JSON body |
| `401` | Not logged in or token expired — login again |
| `403` | Not allowed — you're not admin |
| `404` | Not found — wrong ID or slug |
| `429` | Too many requests — slow down |
