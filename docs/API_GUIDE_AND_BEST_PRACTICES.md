# API Guide & Best Practices Implementation
## E-Commerce Backend REST API

**Base URL:** `https://ecommerce-backend-1-v60x.onrender.com/api/v1/`  
**Documentation:** `https://ecommerce-backend-1-v60x.onrender.com/api/docs/`  
**OpenAPI Schema:** `https://ecommerce-backend-1-v60x.onrender.com/api/schema/`

---

## Table of Contents

1. [API Architecture Overview](#1-api-architecture-overview)
2. [Authentication & Security](#2-authentication--security)
3. [Core API Endpoints](#3-core-api-endpoints)
4. [Request/Response Format](#4-requestresponse-format)
5. [Error Handling](#5-error-handling)
6. [Best Practices Applied](#6-best-practices-applied)
7. [Project-Specific Features](#7-project-specific-features)
8. [Rate Limiting & Performance](#8-rate-limiting--performance)

---

## 1. API Architecture Overview

### 1.1 Layered Architecture

```
┌─────────────────────────────────────┐
│      HTTP Client / Frontend         │
│    (Browser, Mobile App, etc.)      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   REST API Layer (Django Views)     │
│  ✓ Validation, Authentication       │
│  ✓ Serialization, Pagination        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Business Logic Layer             │
│   (Service Classes, Managers)       │
│  ✓ Inventory Management             │
│  ✓ Payment Processing               │
│  ✓ Order Processing                 │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     Data Access Layer (Models)      │
│   ✓ ORM Queries with optimization   │
│   ✓ Atomic Transactions             │
│   ✓ Cache-aware operations          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   PostgreSQL + Redis + S3           │
│      (Data & Cache Storage)         │
└─────────────────────────────────────┘
```

### 1.2 URL Structure (RESTful)

```
/api/v1/
├── auth/              # Authentication & User management
│   ├── register/      # POST (create user)
│   ├── login/         # POST (authenticate)
│   ├── logout/        # POST (revoke token)
│   ├── refresh/       # POST (refresh access token)
│   ├── me/            # GET/PUT (profile)
│   ├── me/addresses/  # GET/POST (user addresses)
│   └── password/      # POST (password operations)
│
├── products/          # Product catalog
│   ├── categories/    # GET (list categories)
│   ├── (/)            # GET (list products)
│   ├── {slug}/        # GET (product details)
│   ├── {slug}/reviews/ # GET/POST (product reviews)
│   └── {slug}/wishlist/ # POST (toggle wishlist)
│
├── cart/              # Shopping cart operations
│   ├── (/)            # GET (cart contents)
│   ├── items/         # POST (add item)
│   ├── items/{id}/    # PUT/DELETE (update/remove item)
│   └── clear/         # POST (clear cart)
│
├── orders/            # Order management
│   ├── (/)            # GET/POST (list/create orders)
│   ├── {id}/          # GET (order details)
│   └── {id}/cancel/   # POST (cancel order)
│
└── payments/          # Payment processing
    ├── create-intent/ # POST (create Stripe intent)
    ├── confirm/       # POST (confirm payment)
    └── webhook/       # POST (Stripe webhook)
```

---

## 2. Authentication & Security

### 2.1 JWT (JSON Web Token) Strategy

**Token Type:** Bearer tokens with asymmetric expiry

```
Access Token:
  - Duration: 1 hour (short-lived)
  - Use: API requests
  - Contains: user_id, username, permissions
  - Location: Authorization header

Refresh Token:
  - Duration: 7 days (long-lived)
  - Use: Generate new access tokens
  - Stored: HTTP-only cookies (secure) or client storage
  - Feature: Blacklist support (logout)

Token Generation Flow:
  1. User registers/logs in
  2. Server creates refresh + access tokens
  3. Client stores access token in memory (short-lived)
  4. Client stores refresh token securely
  5. Before access token expires, use refresh to get new access token
  6. On logout, refresh token is blacklisted
```

### 2.2 Authentication Endpoints

#### Register New User
```http
POST /api/v1/auth/register/
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890"
}

Response (201 Created):
{
  "message": "User registered successfully. Please check your email to verify your account.",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}

Validation Applied:
✓ Email uniqueness check
✓ Password strength validation (uppercase, lowercase, numbers, symbols)
✓ Password confirmation match
✓ Email format validation
✓ Phone number optional
```

#### Login
```http
POST /api/v1/auth/login/
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response (200 OK):
{
  "message": "Login successful",
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": true
  }
}

Validation Applied:
✓ Email/password authentication
✓ Account active status check
✓ JWT token generation with metadata
```

#### Refresh Access Token
```http
POST /api/v1/auth/refresh/
Content-Type: application/json

Request:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

Response (200 OK):
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

Notes:
✓ Token automatically blacklisted after logout
✓ Invalid/expired refresh tokens rejected
```

#### Logout
```http
POST /api/v1/auth/logout/
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}

Response (200 OK):
{
  "message": "Logout successful"
}

Security:
✓ Refresh token blacklisted (cannot be reused)
✓ Further requests with blacklisted token rejected
✓ Server-side token tracking
```

### 2.3 Security Implementation

**Applied Security Measures:**

| Layer | Implementation |
|-------|-----------------|
| **Transport** | HTTPS/TLS only, HSTS headers |
| **Authentication** | JWT with secure signature (HS256) |
| **Authorization** | Permission classes (IsAuthenticated, IsAuthenticatedOrReadOnly) |
| **Token Security** | Short-lived access tokens, refresh token blacklist |
| **CORS** | Whitelist specific domains, prevent cross-origin attacks |
| **CSRF** | Django CSRF tokens for state-changing operations |
| **Input Validation** | DRF serializer validation on all inputs |
| **Rate Limiting** | Throttle auth endpoints to prevent brute force |
| **Secrets** | Environment variables, no hardcoded keys |
| **Password Security** | bcrypt hashing, Django validators (min length, complexity) |

---

## 3. Core API Endpoints

### 3.1 User Management

#### Get User Profile
```http
GET /api/v1/auth/me/
Authorization: Bearer {access_token}

Response (200 OK):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "is_verified": true,
  "created_at": "2024-12-01T10:30:00Z"
}

Permissions: IsAuthenticated
```

#### Update User Profile
```http
PUT /api/v1/auth/me/
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "first_name": "Jane",
  "last_name": "Smith",
  "phone_number": "+0987654321"
}

Response (200 OK):
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone_number": "+0987654321",
  "is_verified": true,
  "created_at": "2024-12-01T10:30:00Z"
}

Permissions: IsAuthenticated
Validation: Email cannot be changed, partial updates allowed
```

#### Address Management
```http
GET /api/v1/auth/me/addresses/
Authorization: Bearer {access_token}

Response (200 OK):
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "address_type": "shipping",
      "full_name": "John Doe",
      "phone_number": "+1234567890",
      "street_address": "123 Main St",
      "apartment": "Apt 4B",
      "city": "New York",
      "state": "NY",
      "country": "USA",
      "zip_code": "10001",
      "is_default": true,
      "created_at": "2024-12-01T10:30:00Z"
    }
  ]
}

Permissions: IsAuthenticated
Pagination: 20 items per page (configurable)
```

#### Create Address
```http
POST /api/v1/auth/me/addresses/
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "address_type": "billing",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "street_address": "456 Oak Ave",
  "city": "Los Angeles",
  "state": "CA",
  "country": "USA",
  "zip_code": "90001",
  "is_default": false
}

Response (201 Created):
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "address_type": "billing",
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "street_address": "456 Oak Ave",
  "apartment": null,
  "city": "Los Angeles",
  "state": "CA",
  "country": "USA",
  "zip_code": "90001",
  "is_default": false,
  "created_at": "2024-12-02T14:45:00Z"
}

Validation:
✓ Required fields: address_type, full_name, street_address, city, country, zip_code
✓ Address type choices: ['shipping', 'billing', 'other']
✓ Phone number format validation
```

---

### 3.2 Product Catalog

#### List Categories
```http
GET /api/v1/products/categories/
Authorization: (optional)

Response (200 OK):
{
  "results": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "name": "Electronics",
      "slug": "electronics",
      "description": "Electronic devices and gadgets",
      "image": "https://bucket.s3.amazonaws.com/electronics.jpg",
      "children": [
        {
          "id": "990e8400-e29b-41d4-a716-446655440004",
          "name": "Laptops",
          "slug": "laptops",
          "description": "Computing devices",
          "children": []
        }
      ]
    }
  ]
}

Features:
✓ Hierarchical structure (parent/child categories)
✓ Cached for 1 hour (improves performance 30x)
✓ Recursive children population
✓ Anonymous access allowed
```

#### List Products (with Filtering & Sorting)
```http
GET /api/v1/products/?category=electronics&min_price=100&max_price=500&in_stock=true&search=laptop&ordering=-created_at&page=1&page_size=20
Authorization: (optional)

Response (200 OK):
{
  "count": 245,
  "next": "https://.../products/?page=2",
  "previous": null,
  "results": [
    {
      "id": "aa0e8400-e29b-41d4-a716-446655440005",
      "name": "MacBook Pro 16\"",
      "slug": "macbook-pro-16",
      "price": "2499.99",
      "compare_price": "2999.99",
      "quantity": 15,
      "is_in_stock": true,
      "is_featured": true,
      "discount_percentage": 17,
      "category": {
        "id": "880e8400-e29b-41d4-a716-446655440003",
        "name": "Electronics"
      },
      "images": [
        {
          "id": "bb0e8400-e29b-41d4-a716-446655440006",
          "image": "https://bucket.s3.amazonaws.com/macbook1.jpg",
          "alt_text": "Front view",
          "is_primary": true
        }
      ],
      "average_rating": 4.8,
      "review_count": 24
    }
  ]
}

Query Parameters:
✓ category: Filter by category slug
✓ min_price, max_price: Price range (decimal values)
✓ in_stock: Boolean filter (true/false)
✓ search: Full-text search (name, description, SKU)
✓ ordering: Sort by price, -price, created_at, -created_at, name
✓ page: Page number (default 1)
✓ page_size: Items per page (default 20, max 100)

Caching: Anonymous users - 5 minutes
Performance: O(log n) with composite indexes
```

#### Get Product Details
```http
GET /api/v1/products/macbook-pro-16/
Authorization: (optional)

Response (200 OK):
{
  "id": "aa0e8400-e29b-41d4-a716-446655440005",
  "name": "MacBook Pro 16\"",
  "slug": "macbook-pro-16",
  "description": "Powerful laptop with M2 Pro chip...",
  "price": "2499.99",
  "compare_price": "2999.99",
  "cost_price": "1500.00",
  "sku": "MBPRO-16-2024",
  "quantity": 15,
  "is_in_stock": true,
  "is_featured": true,
  "weight": "2.1",
  "dimensions": "35 x 24 x 1.6 cm",
  "discount_percentage": 17,
  "category": {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "name": "Electronics"
  },
  "images": [
    {
      "id": "bb0e8400-e29b-41d4-a716-446655440006",
      "image": "https://bucket.s3.amazonaws.com/macbook1.jpg",
      "alt_text": "Front view",
      "is_primary": true,
      "order": 1
    }
  ],
  "variants": [
    {
      "id": "cc0e8400-e29b-41d4-a716-446655440007",
      "name": "16GB RAM - 512GB SSD",
      "sku": "MBPRO-16-512",
      "price": "2499.99",
      "quantity": 10,
      "attributes": {
        "ram": "16GB",
        "storage": "512GB"
      }
    }
  ],
  "reviews": [
    {
      "id": "dd0e8400-e29b-41d4-a716-446655440008",
      "user": "john@example.com",
      "rating": 5,
      "title": "Excellent laptop!",
      "comment": "Very satisfied with the purchase...",
      "is_verified_purchase": true,
      "created_at": "2024-12-01T10:30:00Z"
    }
  ],
  "average_rating": 4.8,
  "created_at": "2024-10-15T08:00:00Z"
}

Features:
✓ Complete product hierarchy (variants, images, reviews)
✓ Cached for anonymous users (5 minutes)
✓ Pre-fetched relationships (no N+1 queries)
✓ Review count and average rating
```

#### Add Product Review
```http
POST /api/v1/products/macbook-pro-16/reviews/
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "rating": 5,
  "title": "Excellent laptop!",
  "comment": "Excellent performance and build quality. Highly recommend!"
}

Response (201 Created):
{
  "id": "dd0e8400-e29b-41d4-a716-446655440008",
  "user": "john@example.com",
  "rating": 5,
  "title": "Excellent laptop!",
  "comment": "Excellent performance and build quality...",
  "is_verified_purchase": true,
  "is_approved": true,
  "created_at": "2024-12-02T15:30:00Z"
}

Validation:
✓ Rating: 1-5 integer
✓ Title: Required, max 200 chars
✓ Comment: Required
✓ User must have purchased product (verified_purchase flag)
✓ One review per user per product
```

#### Wishlist Management
```http
POST /api/v1/products/macbook-pro-16/wishlist/
Authorization: Bearer {access_token}

Response (201 Created):
{
  "message": "Product added to wishlist",
  "in_wishlist": true
}

Second request (toggles):
Response (200 OK):
{
  "message": "Product removed from wishlist",
  "in_wishlist": false
}

Permissions: IsAuthenticated
Uses: Atomic get_or_create pattern (efficient)
```

#### Get User Wishlist
```http
GET /api/v1/products/wishlist/me/?page=1&page_size=20
Authorization: Bearer {access_token}

Response (200 OK):
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "product": {
        "id": "aa0e8400-e29b-41d4-a716-446655440005",
        "name": "MacBook Pro 16\"",
        "slug": "macbook-pro-16",
        "price": "2499.99",
        "quantity": 15,
        "is_in_stock": true
      },
      "added_at": "2024-12-01T10:30:00Z"
    }
  ]
}

Features:
✓ Pagination support
✓ Optimized with select_related (product) and prefetch_related (images)
✓ Ordered by most recent additions
```

---

### 3.3 Shopping Cart

#### Get Cart
```http
GET /api/v1/cart/
Authorization: Bearer {access_token}

Response (200 OK):
{
  "id": "ee0e8400-e29b-41d4-a716-446655440009",
  "items": [
    {
      "id": "ff0e8400-e29b-41d4-a716-446655440010",
      "product": {
        "id": "aa0e8400-e29b-41d4-a716-446655440005",
        "name": "MacBook Pro 16\"",
        "slug": "macbook-pro-16"
      },
      "variant": {
        "id": "cc0e8400-e29b-41d4-a716-446655440007",
        "name": "16GB RAM - 512GB SSD",
        "sku": "MBPRO-16-512"
      },
      "quantity": 1,
      "price": "2499.99",
      "total_price": "2499.99"
    }
  ],
  "total_items": 1,
  "subtotal": "2499.99",
  "created_at": "2024-12-01T10:30:00Z",
  "updated_at": "2024-12-02T15:30:00Z"
}

Features:
✓ Automatic cart creation (get_or_create pattern)
✓ Denormalized totals (O(1) complexity)
✓ Pre-fetched relationships (no N+1 queries)
✓ Atomic operations for concurrent safety
```

#### Add Item to Cart
```http
POST /api/v1/cart/items/
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "product_id": "aa0e8400-e29b-41d4-a716-446655440005",
  "variant_id": "cc0e8400-e29b-41d4-a716-446655440007",
  "quantity": 2
}

Response (201 Created):
{
  "id": "ff0e8400-e29b-41d4-a716-446655440010",
  "product": {
    "id": "aa0e8400-e29b-41d4-a716-446655440005",
    "name": "MacBook Pro 16\""
  },
  "variant": {
    "id": "cc0e8400-e29b-41d4-a716-446655440007",
    "name": "16GB RAM - 512GB SSD"
  },
  "quantity": 2,
  "price": "2499.99",
  "total_price": "4999.98"
}

Second request (same product):
{
  "message": "Item quantity updated",
  "quantity": 4,  # Accumulated (2 + 2)
  "total_price": "9999.96"
}

Algorithm: Atomic upsert pattern
✓ If item exists: increment quantity (single UPDATE)
✓ If item doesn't exist: create (single INSERT)
✓ Inventory validation (has_stock)
```

#### Update Cart Item
```http
PUT /api/v1/cart/items/ff0e8400-e29b-41d4-a716-446655440010/
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "quantity": 3
}

Response (200 OK):
{
  "id": "ff0e8400-e29b-41d4-a716-446655440010",
  "product": {...},
  "quantity": 3,
  "price": "2499.99",
  "total_price": "7499.97"
}

Validation:
✓ Quantity must be positive integer
✓ Cannot exceed product stock
✓ Belongs to current user's cart
```

#### Remove Cart Item
```http
DELETE /api/v1/cart/items/ff0e8400-e29b-41d4-a716-446655440010/
Authorization: Bearer {access_token}

Response (204 No Content)

Side Effect:
✓ Item deleted from cart
✓ Cart totals updated via signal
```

#### Clear Cart
```http
POST /api/v1/cart/clear/
Authorization: Bearer {access_token}

Response (200 OK):
{
  "message": "Cart cleared successfully"
}

Implementation:
✓ Bulk delete of all cart items
✓ Atomic operation (transaction-safe)
```

---

### 3.4 Orders

#### Create Order (Checkout)
```http
POST /api/v1/orders/
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "shipping_address_id": "660e8400-e29b-41d4-a716-446655440001",
  "billing_address_id": "770e8400-e29b-41d4-a716-446655440002"
}

Response (201 Created):
{
  "id": "880e8400-e29b-41d4-a716-446655440010",
  "order_number": "ORD-20241202-ABC123",
  "status": "pending",
  "subtotal": "2499.99",
  "tax": "249.99",
  "shipping_cost": "5.00",
  "discount": "0.00",
  "total_amount": "2754.98",
  "items": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440011",
      "product_name": "MacBook Pro 16\"",
      "product_sku": "MBPRO-16-512",
      "price": "2499.99",
      "quantity": 1,
      "subtotal": "2499.99"
    }
  ],
  "shipping_address": {...},
  "billing_address": {...},
  "created_at": "2024-12-02T16:00:00Z"
}

Algorithm (Atomic Transaction):
  1. Validate cart has items
  2. Calculate: subtotal, tax (10%), shipping ($5)
  3. Create Order with all fields
  4. Bulk create OrderItems (snapshot at time)
  5. Bulk update Product quantities (F-expressions)
  6. Clear user's cart
  7. Create OrderStatusHistory entry
  ✓ All within @transaction.atomic

Validation:
✓ User has valid cart with items
✓ Addresses belong to user
✓ Stock available for all items
✓ Shipping & billing addresses required

Features:
✓ Immutable order snapshot (prevents future price changes)
✓ Atomic transaction (all-or-nothing)
✓ Inventory deduction (track_inventory=true)
✓ Order status history tracking
```

#### List User Orders
```http
GET /api/v1/orders/?page=1&ordering=-created_at
Authorization: Bearer {access_token}

Response (200 OK):
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440010",
      "order_number": "ORD-20241202-ABC123",
      "status": "processing",
      "total_amount": "2754.98",
      "item_count": 1,
      "created_at": "2024-12-02T16:00:00Z",
      "updated_at": "2024-12-02T17:00:00Z"
    }
  ]
}

Optimization:
✓ Prefetch: OrderItems, OrderStatusHistory, Addresses
✓ Select_related: User relationships
✓ Indexed queries on user & created_at
```

#### Get Order Details
```http
GET /api/v1/orders/880e8400-e29b-41d4-a716-446655440010/
Authorization: Bearer {access_token}

Response (200 OK):
{
  "id": "880e8400-e29b-41d4-a716-446655440010",
  "order_number": "ORD-20241202-ABC123",
  "status": "processing",
  "subtotal": "2499.99",
  "tax": "249.99",
  "shipping_cost": "5.00",
  "discount": "0.00",
  "total_amount": "2754.98",
  "items": [
    {
      "id": "990e8400-e29b-41d4-a716-446655440011",
      "product_name": "MacBook Pro 16\"",
      "product_sku": "MBPRO-16-512",
      "variant_name": "16GB RAM - 512GB SSD",
      "price": "2499.99",
      "quantity": 1,
      "subtotal": "2499.99"
    }
  ],
  "shipping_address": {
    "full_name": "John Doe",
    "street_address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "zip_code": "10001"
  },
  "billing_address": {...},
  "status_history": [
    {
      "status": "pending",
      "note": "Order created",
      "created_at": "2024-12-02T16:00:00Z"
    },
    {
      "status": "processing",
      "note": "Payment confirmed. Order processing started.",
      "created_at": "2024-12-02T17:00:00Z"
    }
  ],
  "tracking_number": null,
  "shipped_at": null,
  "delivered_at": null,
  "created_at": "2024-12-02T16:00:00Z"
}

Features:
✓ Complete order history
✓ Status tracking timeline
✓ Address snapshot (immutable)
```

#### Cancel Order
```http
POST /api/v1/orders/880e8400-e29b-41d4-a716-446655440010/cancel/
Authorization: Bearer {access_token}

Response (200 OK):
{
  "message": "Order cancelled successfully",
  "order": {
    "id": "880e8400-e29b-41d4-a716-446655440010",
    "status": "cancelled",
    "created_at": "2024-12-02T16:00:00Z"
  }
}

Constraints:
✓ Can only cancel: pending, processing status
✓ Cannot cancel: shipped, delivered, already_cancelled
✓ Inventory restored (F-expressions)
✓ Status history updated
✓ Notification email sent (async)

Error (400 Bad Request):
{
  "error": "Cannot cancel order in shipped status"
}
```

---

### 3.5 Payments

#### Create Payment Intent
```http
POST /api/v1/payments/create-intent/
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "order_id": "880e8400-e29b-41d4-a716-446655440010"
}

Response (200 OK):
{
  "client_secret": "pi_1234567890_secret_abcdef",
  "payment_intent_id": "pi_1234567890"
}

Process:
  1. Fetch order (validate user owns it)
  2. Create Stripe PaymentIntent
    - Amount: order.total_amount * 100 (in cents)
    - Currency: USD
    - Metadata: order_id, customer_email
  3. Create Payment record in database
  4. Return client_secret for frontend Stripe integration

Security:
✓ Amount pulled from Order (prevents tampering)
✓ User ownership validated
✓ Metadata for reconciliation
```

#### Confirm Payment
```http
POST /api/v1/payments/confirm/
Authorization: Bearer {access_token}
Content-Type: application/json

Request:
{
  "order_id": "880e8400-e29b-41d4-a716-446655440010",
  "payment_intent_id": "pi_1234567890"
}

Response (200 OK):
{
  "message": "Payment confirmed successfully",
  "order_id": "880e8400-e29b-41d4-a716-446655440010"
}

Process:
  1. Retrieve PaymentIntent from Stripe
  2. Check status = "succeeded"
  3. Update Payment record with:
     - status = "completed"
     - transaction_id = Stripe intent ID
     - payment_date = now()
     - metadata = Stripe charge info
  4. Update Order status = "processing"
  5. Create OrderStatusHistory entry
  6. Send confirmation email (async)

Error (400 Bad Request):
{
  "error": "Payment not completed",
  "status": "requires_payment_method"
}
```

#### Stripe Webhook
```http
POST /api/v1/payments/webhook/
Content-Type: application/json
X-Stripe-Signature: {signature}

Webhook Events Handled:
- payment_intent.succeeded
- payment_intent.payment_failed
- charge.refunded

Implementation:
✓ Signature verification (Stripe secret)
✓ Idempotency (event ID tracking)
✓ Async processing (Celery task)
✓ Retry logic (exponential backoff)

Response (200 OK):
{
  "status": "success"
}
```

---

## 4. Request/Response Format

### 4.1 Standard Response Structure

**Success (2xx):**
```json
{
  "message": "Operation successful",
  "data": { ... }
}
```

**Pagination (List endpoints):**
```json
{
  "count": 245,
  "next": "https://.../products/?page=2",
  "previous": null,
  "results": [ ... ]
}
```

**Error (4xx/5xx):**
```json
{
  "error": "Error message",
  "code": "error_code",
  "details": { ... }
}
```

### 4.2 Content Negotiation

```
Accept: application/json          # Required (API is JSON-only)
Content-Type: application/json    # For POST/PUT/PATCH
Authorization: Bearer {token}     # For authenticated endpoints
```

### 4.3 Data Types

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| id | UUID | 550e8400-e29b-41d4-a716-446655440000 | Primary key |
| email | Email | user@example.com | Lowercase, unique |
| price | Decimal | 2499.99 | 2 decimal places |
| quantity | Integer | 5 | Non-negative |
| rating | Integer | 4 | 1-5 range |
| slug | String | macbook-pro-16 | URL-safe |
| timestamp | ISO8601 | 2024-12-02T16:00:00Z | UTC timezone |
| boolean | Boolean | true / false | Lowercase |

---

## 5. Error Handling

### 5.1 HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 OK | Request succeeded | GET product details |
| 201 Created | Resource created | POST register user |
| 204 No Content | Success, no body | DELETE cart item |
| 400 Bad Request | Invalid input | Missing required field |
| 401 Unauthorized | Missing/invalid token | No Authorization header |
| 403 Forbidden | Lacks permission | Accessing others' data |
| 404 Not Found | Resource doesn't exist | Non-existent product |
| 409 Conflict | Data conflict | Duplicate unique value |
| 429 Too Many Requests | Rate limit exceeded | Too many login attempts |
| 500 Server Error | Server fault | Database connection error |

### 5.2 Error Response Format

```json
{
  "error": "Invalid input",
  "code": "validation_error",
  "details": {
    "email": ["Enter a valid email address."],
    "password": ["Password must be at least 8 characters."],
    "quantity": ["Quantity must be greater than 0."]
  }
}
```

### 5.3 Common Errors

**Invalid Token:**
```json
{
  "error": "Token is invalid or expired",
  "code": "invalid_token",
  "details": null
}
```

**Rate Limited:**
```json
{
  "error": "Request throttled. Retry after 60 seconds.",
  "code": "throttled",
  "retry_after": 60
}
```

**Out of Stock:**
```json
{
  "error": "Insufficient stock",
  "code": "stock_unavailable",
  "details": {
    "requested": 5,
    "available": 2
  }
}
```

---

## 6. Best Practices Applied

### 6.1 REST Principles

#### Resource-Oriented Design
```
✓ Use nouns for endpoints (/products, not /getProducts)
✓ Use HTTP verbs for operations (GET, POST, PUT, DELETE)
✓ Hierarchical URLs (/orders/{id}/items/{item_id})
✓ Stateless operations (each request contains all info)
```

#### HTTP Methods (CRUD)
```
POST   /products/           Create (201 Created)
GET    /products/           Read list (200 OK)
GET    /products/{id}/      Read one (200 OK)
PUT    /products/{id}/      Update (200 OK)
DELETE /products/{id}/      Delete (204 No Content)
```

### 6.2 Input Validation

**Serializer-Level Validation:**
```python
class UserRegistrationSerializer(ModelSerializer):
    password = CharField(
        write_only=True,
        validators=[validate_password]  # Django's password validators
    )
    password_confirm = CharField(write_only=True)
    
    def validate(self, attrs):
        """Cross-field validation"""
        if attrs['password'] != attrs['password_confirm']:
            raise ValidationError("Passwords must match")
        return attrs
```

**Field-Level Validation:**
```python
email = EmailField()  # Validates format
rating = IntegerField(min_value=1, max_value=5)
quantity = IntegerField(min_value=1)
```

**Database-Level Validation:**
```python
class Product(Model):
    sku = CharField(max_length=100, unique=True)  # Unique constraint
    price = DecimalField(validators=[MinValueValidator(0)])
```

### 6.3 Authentication & Authorization

**JWT Token Pattern:**
```python
class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Validate credentials
        user = authenticate(email=email, password=password)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        # Return with expiry info
        return Response({
            'access': str(access),
            'refresh': str(refresh),
            'expires_in': 3600  # 1 hour
        })
```

**Permission Classes:**
```python
class CartDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]  # Only logged-in users
    
    def get_object(self):
        return self.request.user.cart  # Auto-scoped to current user

class ProductListView(ListAPIView):
    permission_classes = [AllowAny]  # Public read access
```

### 6.4 Clean Architecture

**Separation of Concerns:**
```
Views (HTTP handling)
  ↓
Serializers (Data validation & transformation)
  ↓
Business Logic (Services/Managers)
  ↓
Models (Data persistence)
```

**InventoryManager Pattern:**
```python
class InventoryManager:
    """Encapsulates inventory business logic"""
    
    @staticmethod
    def allocate_stock(product_id, quantity):
        """Atomic inventory deduction"""
        return Product.objects.filter(
            id=product_id,
            quantity__gte=quantity
        ).update(quantity=F('quantity') - quantity)

# Usage in views:
if InventoryManager.allocate_stock(product_id, qty):
    # Success
else:
    # Out of stock
```

**Signal-Based Events:**
```python
@receiver(post_save, sender=CartItem)
def update_cart_totals(sender, instance, **kwargs):
    """Denormalize cart totals when items change"""
    instance.cart.update_cache()

# Benefits:
# ✓ Decoupled logic
# ✓ Reusable across app
# ✓ Automatic side effects
```

### 6.5 Error Handling

**Consistent Error Format:**
```python
def toggle_wishlist(request, slug):
    try:
        product = Product.objects.get(slug=slug)
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
```

**Validation Errors:**
```python
serializer = ProductSerializer(data=request.data)
if not serializer.is_valid():
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
```

**Atomic Transactions:**
```python
@transaction.atomic
def perform_create(self, serializer):
    """Order creation - all or nothing"""
    # Create order
    # Bulk create items
    # Update inventory
    # If any step fails, all rollback
```

---

## 7. Project-Specific Features

### 7.1 Checkout Flow (End-to-End)

```
1. User Adds Items to Cart
   └─ POST /cart/items/
      - Atomic upsert (get_or_create)
      - Inventory validation
      - Cart updated via signal

2. User Proceeds to Checkout
   └─ POST /orders/
      - Validates addresses
      - Calculates: subtotal, tax (10%), shipping ($5)
      - Creates immutable order snapshot
      - Bulk creates order items
      - Bulk updates product quantities (F-expressions)
      - Clears cart
      - All within @transaction.atomic

3. User Initiates Payment
   └─ POST /payments/create-intent/
      - Creates Stripe PaymentIntent
      - Returns client_secret for frontend

4. User Completes Payment (Frontend)
   └─ Stripe.js confirms payment with client_secret

5. Server Confirms Payment
   └─ POST /payments/confirm/
      - Verifies Stripe PaymentIntent status
      - Updates Payment record
      - Updates Order status → "processing"
      - Creates OrderStatusHistory
      - Sends confirmation email (async)

6. Order Fulfillment
   └─ Admin ships order
      - Update Order.status → "shipped"
      - Set tracking_number, shipped_at
      - Send shipping notification email

7. Delivery Confirmation
   └─ Webhook from carrier or manual update
      - Update Order.status → "delivered"
      - Set delivered_at
      - Send delivery confirmation email
```

### 7.2 Inventory Management

**Stock Tracking:**
```python
# Every CartItem addition checks stock:
if not InventoryManager.check_availability(product_id, qty):
    return Response({'error': 'Out of stock'}, 400)

# Every Order creation deducts stock (atomic):
Product.objects.filter(id=pid).update(
    quantity=F('quantity') - qty  # Database-level atomicity
)

# Every Order cancellation restores stock:
Product.objects.filter(id=pid).update(
    quantity=F('quantity') + qty
)
```

**Low Stock Alerts:**
```python
# Signal-based (event-driven):
@receiver(post_save, sender=Product)
def check_low_stock(sender, instance, **kwargs):
    if instance.is_low_stock:
        send_low_stock_alert.delay(instance.id)

# Efficient query:
low_stock = InventoryManager.get_low_stock_products(threshold=10)
# Returns products with quantity ≤ threshold
# Uses O(n) query with index optimization
```

### 7.3 Search & Filtering

**Full-Text Search:**
```python
# Frontend query:
GET /products/?search=macbook

# Backend algorithm:
1. Tokenize search term: "macbook"
2. Search indexed fields: name, description, sku
3. Use PostgreSQL full-text search (O(log n) with GIN index)
4. Rank results by relevance
5. Return sorted by rank
```

**Composite Filtering:**
```python
# Complex query combining multiple filters:
GET /products/?category=electronics&min_price=100&max_price=500&in_stock=true&search=laptop

# Query optimization:
- Index on [category, is_active] → category filter
- Index on [is_active, quantity] → stock filter
- Full-text index on [name, description] → search
- Price range uses B-tree index
→ All filters executed at database level
→ Zero application-level filtering
```

### 7.4 Product Variants & Pricing

**Variant Hierarchy:**
```
Product (base)
├── price (default)
├── Variant 1: 16GB RAM - 512GB SSD
│   └── price (overrides product.price)
├── Variant 2: 32GB RAM - 1TB SSD
│   └── price (overrides product.price)
└── Variant 3: 8GB RAM - 256GB SSD
    └── price (overrides product.price)
```

**Effective Price Calculation:**
```python
@property
def effective_price(self):
    """Returns variant price if set, otherwise product price"""
    return self.price if self.price else self.product.price

# Usage in cart:
cart_item.price = variant.effective_price  # Snapshot at purchase
```

### 7.5 Order Status Tracking

**Immutable Status History:**
```python
class OrderStatusHistory(Model):
    order = ForeignKey(Order)
    status = CharField(choices=[...])
    note = TextField()
    created_by = ForeignKey(User, null=True)
    created_at = DateTimeField(auto_now_add=True)

# Every status change creates new history entry:
1. Order created → pending
2. Payment confirmed → processing
3. Shipped → shipped (with tracking number)
4. Delivered → delivered
5. (Optional) Returned → returned
```

**Status Validation:**
```python
# Only certain transitions allowed:
def update_order_status(order, new_status):
    allowed = {
        'pending': ['processing', 'cancelled'],
        'processing': ['shipped', 'cancelled'],
        'shipped': ['delivered'],
        'delivered': ['returned'],
        'cancelled': [],  # Terminal state
        'returned': []    # Terminal state
    }
    
    if new_status not in allowed.get(order.status, []):
        raise ValidationError(f"Cannot change from {order.status} to {new_status}")
```

---

## 8. Rate Limiting & Performance

### 8.1 Rate Limiting

**Authentication Endpoints (Strict):**
```python
# Max 5 login attempts per 15 minutes
class LoginThrottle(UserRateThrottle):
    scope = 'login'
    rate = '5/15m'

# Max 3 registration attempts per hour
class RegisterThrottle(UserRateThrottle):
    scope = 'register'
    rate = '3/h'
```

**API Endpoints (Moderate):**
```python
# Max 100 requests per minute for authenticated users
class APIThrottle(UserRateThrottle):
    scope = 'api'
    rate = '100/m'

# Max 20 requests per minute for anonymous users
class AnonThrottle(AnonRateThrottle):
    scope = 'anon'
    rate = '20/m'
```

### 8.2 Caching Strategy

**Category Hierarchy (1 hour):**
```python
cache_key = 'categories_list_root'
categories = cache.get(cache_key)

if categories is None:
    # Expensive hierarchical query
    categories = Category.objects.filter(...).prefetch_related(...)
    cache.set(cache_key, list(categories), 3600)
```

**Product Details (5 minutes, anonymous only):**
```python
if not request.user.is_authenticated:
    cache_key = f'product_detail_{slug}'
    cached = cache.get(cache_key)
    
    if cached:
        return Response(cached)

# ... fetch and cache if not authenticated
```

**Cache Invalidation:**
```python
# When review is added, invalidate product cache:
@receiver(post_save, sender=Review)
def invalidate_product_cache(sender, instance, **kwargs):
    cache.delete(f'product_detail_{instance.product.slug}')
```

### 8.3 Query Optimization

**N+1 Query Prevention:**
```python
# ✅ CORRECT - Single query with joins:
products = Product.objects.filter(is_active=True).select_related(
    'category'  # JOIN category
).prefetch_related(
    'images',   # Separate query for all images
    Prefetch('reviews', queryset=Review.objects.filter(is_approved=True))
)

# ❌ WRONG - N+1 queries:
products = Product.objects.filter(is_active=True)
for p in products:
    print(p.category.name)  # New query per product!
```

**Pagination:**
```python
# Fetch only needed data:
products = Product.objects.only(
    'id', 'name', 'slug', 'price', 'quantity'
).filter(...)[0:20]  # Limit to page size
```

**Batch Operations:**
```python
# ✅ Bulk create (1 query):
OrderItem.objects.bulk_create(order_items)  # 100 items = 1 INSERT

# ❌ Individual creates (100 queries):
for item in order_items:
    OrderItem.objects.create(...)
```

---

## 9. Testing API Locally

### 9.1 Using cURL

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "first_name": "John"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'

# Get products (with token)
curl -X GET "http://localhost:8000/api/v1/products/?page=1" \
  -H "Authorization: Bearer {access_token}"

# Add to cart
curl -X POST http://localhost:8000/api/v1/cart/items/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "product-uuid",
    "quantity": 1
  }'
```

### 9.2 Using Postman

1. Import OpenAPI schema: `http://localhost:8000/api/schema/`
2. Create environment with `access_token` variable
3. Use pre-request script to refresh token automatically
4. Test collections organized by feature

### 9.3 Using Swagger UI

Visit: `http://localhost:8000/api/docs/`
- Try endpoints directly in browser
- View request/response models
- Download OpenAPI JSON

---

## Summary: Key Implementation Patterns

| Pattern | Implementation | Benefit |
|---------|---|---|
| **JWT Auth** | Short-lived access + refresh tokens | Stateless, scalable |
| **Serializer Validation** | Field + object-level validators | Consistent error handling |
| **Atomic Transactions** | @transaction.atomic on checkout | Data integrity |
| **F-Expressions** | Database-level operations | Concurrency-safe |
| **Bulk Operations** | bulk_create, bulk_update | Performance (1 query vs n) |
| **Prefetch/Select Related** | Query optimization | Prevent N+1 queries |
| **Signal-Based Events** | Post-save/post-delete handlers | Decoupled architecture |
| **Caching** | Redis with TTL | 30x faster on cache hit |
| **Permission Classes** | IsAuthenticated, IsAuthenticatedOrReadOnly | Clean authorization |
| **Pagination** | Offset-based with limit | Standardized API |

