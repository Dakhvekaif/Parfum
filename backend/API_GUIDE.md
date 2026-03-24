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

### Google Login
```
POST /api/auth/google/
```
```json
{ "id_token": "eyJhbGciOiJSUzI1NiIsImt..." }
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

### Contact Us
```
POST /api/contact/
```
```json
{
  "full_name": "John Doe",
  "email": "johndoe@example.com",
  "subject": "Question about shipping",
  "message": "Do you ship to Switzerland?"
}
```
**Response:** `201 Created` with the saved message object.

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
| `search` | `?search=rose` | Quick search on name & inspired_by (use `/api/search/` for full results) |
| `min_price` | `?min_price=1000` | Products with at least one variant ≥ ₹1000 |
| `max_price` | `?max_price=3000` | Products with at least one variant ≤ ₹3000 |
| `ordering` | `?ordering=name` | Sort: `name`, `-created_at`, `avg_rating` |
| `page` | `?page=2` | Pagination (20/page) |

**Response (each product):**
```json
{
  "id": 1,
  "name": "Alpine Noir EDP",
  "slug": "alpine-noir-edp",
  "inspired_by": "Our Creation Of Bdk's Vanille Leather Perfume",
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

### New Arrivals
```
GET /api/products/new-arrivals/
```
**Response:** Same as Product List, but strictly returns active products added within the last 30 days (newest first).

---

### Tester Boxes
```
GET /api/products/tester-boxes/
```
**Public View Response:** Returns a list of all active tester boxes (e.g., "Tester Box 5", "Tester Box 10").
The `products` array inside each box is **automatically filtered by the backend** so that it *only contains the 5ml variant* for each product. Your frontend does not need to filter the variant sizes manually!

```json
[
  {
    "id": 1,
    "name": "Tester Box 5",
    "slug": "tester-box-5",
    "description": "Our curated 5-piece sample box.",
    "created_at": "2026-03-12T10:00:00Z",
    "products": [
      {
        "id": 15,
        "name": "Midnight Rose Parfum",
        "slug": "midnight-rose-parfum",
        "starting_price": "499.00",
        "category": { "id": 2, "name": "Women", "slug": "women" },
        "primary_image": { "id": 22, "image": "...", "alt_text": "..." },
        "variants": [
          {
            "id": 45,
            "quantity_ml": 5,
            "india_price": "499.00",
            "india_discount_price": null,
            "india_effective_price": "499.00",
            "in_stock": true
          }
        ]
      }
    ]
  }
]
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

## 🧴 ROLL ON ATTARS (No auth needed)

Roll-on attars are **separate** from the main product catalogue and **not returned** by `/api/products/`. They are always in **10ml** size.

### Roll On List
```
GET /api/roll-ons/
```
**Optional query params:**
| Param | Example | What it does |
|-------|---------|--------------|
| `search` | `?search=musk` | Search by name or inspired_by |
| `ordering` | `?ordering=-avg_rating` | Sort: `name`, `-created_at`, `avg_rating` |

**Response:** Array of roll-on products (same shape as Product List, with `is_roll_on: true` and a single 10ml variant).

---

### Roll On Detail
```
GET /api/roll-ons/{slug}/
```
**Response:** Full product detail — same as `/api/products/{slug}/`  but for a roll-on.

---


```
GET /api/search/?q={query}
```
> No auth needed. Searches product `name` **and** `inspired_by` fields (case-insensitive).  
> Returns **full product detail** — variants, images, category, collections all included.  
> All params are optional — you can use price filters alone without a text query.

**Query params:**
| Param | Example | What it does |
|-------|---------|--------------|
| `q` | `?q=oud` | Search by name or inspired_by |
| `min_price` | `?min_price=500` | Only products with a variant ≥ ₹500 |
| `max_price` | `?max_price=1000` | Only products with a variant ≤ ₹1000 |

**Examples:**
```
GET /api/search/?q=oud
GET /api/search/?q=rose&max_price=1500
GET /api/search/?max_price=1000            ← "under ₹1000" browse
GET /api/search/?min_price=500&max_price=2000
```

**Response:**
```json
{
  "query": "oud",
  "count": 2,
  "results": [
    {
      "id": 1,
      "name": "Alpine Noir EDP",
      "slug": "alpine-noir-edp",
      "inspired_by": "Our Creation Of Creed's Royal Oud",
      "description": "...",
      "starting_price": "999.00",
      "in_stock": true,
      "avg_rating": "4.50",
      "category": { "id": 1, "name": "Men", "slug": "men" },
      "collections": [ { "id": 1, "name": "Indian Products", "slug": "indian-products" } ],
      "images": [
        { "id": 1, "image": "https://...", "alt_text": "Alpine Noir", "sort_order": 0 }
      ],
      "variants": [
        { "id": 1, "quantity_ml": 10, "india_price": "999.00", "india_discount_price": null, "india_effective_price": "999.00", "india_discount_percentage": 0, "india_stock": 40, "india_in_stock": true, "switzerland_price": "15.00", "switzerland_effective_price": "15.00", "switzerland_stock": 10, "switzerland_in_stock": true, "in_stock": true }
      ],
      "created_at": "2026-01-15T10:00:00Z",
      "updated_at": "2026-02-01T08:00:00Z"
    }
  ]
}
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

### Pricing Preview (Before Checkout) 🔒

Use these endpoints to show the user a full pricing breakdown (Subtotal, Discount, GST 18%, Shipping) **before** they proceed to payment. They do not create any orders.

#### Cart Preview
```
POST /api/orders/cart-preview/
```
```json
{
  "discount_code": "WELCOME10" // Optional
}
```

#### Buy Now Preview
```
POST /api/orders/buynow-preview/
```
```json
{
  "variant_id": 3,
  "quantity": 1,
  "selected_origin": "india",
  "discount_code": "" // Optional
}
```

**Response (Both):**
```json
{
  "subtotal": 2999.0,
  "discount_amount": 0.0,
  "gst_amount": 539.82,
  "shipping_fee": 0.0,
  "total_amount": 3538.82,
  "free_shipping_threshold": 499,
  "items": [
    {
      "product_name": "Alpine Noir EDP",
      "quantity_ml": 50,
      "selected_origin": "india",
      "quantity": 1,
      "unit_price": 2999.0,
      "line_total": 2999.0
    }
  ]
}
```

---

### Step 1: Checkout (Cart → Order)
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

**Response for online payments (UPI/card/wallet/netbanking):**
```json
{
  "id": 5,
  "order_number": "...",
  "total_amount": "2999.00",
  "razorpay_order_id": "order_xxxxxxx",
  "razorpay_key_id": "rzp_test_xxxxxxx",
  "amount_paise": 299900,
  "currency": "INR",
  "items": [...],
  "payment": { "status": "pending", "razorpay_order_id": "order_xxxxxxx" }
}
```

**Response for COD:** Same order object but WITHOUT `razorpay_*` fields (no popup needed).

---

### Buy Now (Direct Single-Product Checkout) 🔒
```
POST /api/orders/buy-now/
```
```json
{
  "variant_id": 3,
  "quantity": 1,
  "shipping_name": "Rahul Sharma",
  "shipping_address": "12 MG Road, Bandra West",
  "shipping_city": "Mumbai",
  "shipping_pincode": "400001",
  "shipping_phone": "9876543210",
  "payment_method": "upi"
}
```
> **Skips cart entirely** — creates a single-item order directly.
> Response is identical to checkout (includes `razorpay_*` fields for online payments).
> Use this for the "Buy Now" button on the product page.

---

### Step 2: Open Razorpay Popup (Frontend)
After checkout returns `razorpay_order_id` and `razorpay_key_id`, open the Razorpay popup:
```javascript
// Add <script src="https://checkout.razorpay.com/v1/checkout.js"></script> to your HTML

const options = {
  key: response.razorpay_key_id,         // from checkout response
  amount: response.amount_paise,          // in paise
  currency: response.currency,            // "INR"
  order_id: response.razorpay_order_id,   // from checkout response
  name: "Parfum",
  description: "Order Payment",
  handler: function (paymentResponse) {
    // paymentResponse has: razorpay_payment_id, razorpay_order_id, razorpay_signature
    // Send these to Step 3 (verify-payment)
    verifyPayment(response.id, paymentResponse);
  },
  prefill: {
    name: "Rahul Sharma",
    email: "rahul@example.com",
    contact: "9876543210"
  },
  theme: { color: "#000000" }
};
const rzp = new Razorpay(options);
rzp.open();
```

---

### Step 3: Verify Payment (After Popup)
```
POST /api/orders/{order_id}/verify-payment/
```
```json
{
  "razorpay_payment_id": "pay_xxxxxxxx",
  "razorpay_order_id": "order_xxxxxxxx",
  "razorpay_signature": "xxxxxxxxxxxxxxx"
}
```
> All 3 values come from Razorpay popup's `handler` callback.

**Response (success):**
```json
{
  "message": "Payment verified successfully!",
  "order": { "id": 5, "status": "confirmed", "payment": { "status": "completed" } }
}
```

**Response (invalid signature):**
```json
{ "error": "Payment verification failed — invalid signature." }
```

### Step 4: What to Show on Frontend After Payment

**If verify-payment returns 200 (success):**
- Show **"Payment Successful! 🎉"** page
- Display order details from `response.order`: order number, items, total, status
- Redirect to order history or a "Thank You" page

**If verify-payment returns 400 (failed):**
- Show **"Payment Failed"** message
- Let user retry — their cart/order is still there

**If user closes Razorpay popup without paying:**
- No need to call verify-payment
- The order stays as `"pending"` — user can retry later
- For checkout flow: cart items are preserved (not cleared until payment succeeds)

**Order lifecycle after payment:**
```
pending → confirmed (auto, on payment) → shipped (admin) → delivered (admin)
```

---

### Order History
```
GET /api/orders/
```
**Response:**
```json
[
  { "id": 1, "order_number": "...", "status": "confirmed", "status_display": "Confirmed", "total_amount": "2999.00", "item_count": 2, "created_at": "..." }
]
```

---

### Order Detail
```
GET /api/orders/{id}/
```
**Response:** Full order with `items[]` (each has `product_name`, `quantity_ml`, `quantity`, `price_at_purchase`, `line_total`) + `payment` info.

---

### Record Payment (Manual/COD)
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

### Testing Google Login in Postman
To test the Google Login endpoint (`/api/auth/google/`) using Postman, you cannot generate a valid `id_token` yourself, as it must be signed by Google. You have two options:
1. **Frontend Integration:** Implement the Google Sign-In button on your React frontend using a library like `@react-oauth/google`. Complete the login flow in your browser, capture the `credential` (which is the `id_token`) from the success callback using `console.log()` or the Network tab, and paste it into Postman as the `id_token` in your Request body.
2. **Google OAuth Playground:** Go to the [Google OAuth 2.0 Playground](https://developers.google.com/oauthplayground/). In step 1, select the "Google OAuth2 API v2" -> "https://www.googleapis.com/auth/userinfo.email" and "https://www.googleapis.com/auth/userinfo.profile" scopes. Complete the authorization flow to get an ID token, and use that in Postman.

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
| `GET/POST/PATCH/DELETE` | `/api/admin/tester-boxes/` | Manage tester box groupings |
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
