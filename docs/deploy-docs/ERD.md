# E-Commerce Backend - Entity Relationship Diagram (ERD)

## ASCII ERD Visualization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         E-COMMERCE DATABASE SCHEMA                          │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌──────────────────┐
                              │      USER        │
                              ├──────────────────┤
                              │ • id (PK)        │
                              │ • email          │
                              │ • username       │
                              │ • first_name     │
                              │ • last_name      │
                              │ • password       │
                              │ • is_active      │
                              │ • is_staff       │
                              │ • created_at     │
                              │ • updated_at     │
                              └────────┬─────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    │                  │                  │
         ┌──────────▼────────┐  ┌──────▼──────────┐  ┌───▼──────────────┐
         │    ADDRESS        │  │ EMAIL_VERIFY    │  │  PASSWORD_RESET  │
         ├──────────────────┤  ├─────────────────┤  ├──────────────────┤
         │ • id (PK)        │  │ • id (PK)       │  │ • id (PK)        │
         │ • user_id (FK)   │  │ • user_id (FK)  │  │ • user_id (FK)   │
         │ • street         │  │ • token         │  │ • token          │
         │ • city           │  │ • created_at    │  │ • created_at     │
         │ • state          │  │ • expires_at    │  │ • expires_at     │
         │ • zip_code       │  └─────────────────┘  └──────────────────┘
         │ • country        │
         │ • is_default     │
         │ • created_at     │
         └──────────────────┘

                              ┌──────────────────┐
                              │    CATEGORY      │
                              ├──────────────────┤
                              │ • id (PK)        │
                              │ • name           │
                              │ • slug           │
                              │ • description    │
                              │ • image          │
                              │ • is_active      │
                              │ • created_at     │
                              │ • updated_at     │
                              └────────┬─────────┘
                                       │
                                       │ 1:N
                                       │
                    ┌──────────────────▼──────────────────┐
                    │         PRODUCT                     │
                    ├─────────────────────────────────────┤
                    │ • id (PK)                           │
                    │ • category_id (FK)                  │
                    │ • name                              │
                    │ • slug                              │
                    │ • description                       │
                    │ • price                             │
                    │ • sku                               │
                    │ • quantity                          │
                    │ • is_featured                       │
                    │ • is_active                         │
                    │ • created_at                        │
                    │ • updated_at                        │
                    └────────────┬─────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                │                │                │
    ┌───────────▼────────┐  ┌───▼──────────┐  ┌─▼────────────────┐
    │  PRODUCT_IMAGE     │  │  VARIANT     │  │     REVIEW       │
    ├────────────────────┤  ├──────────────┤  ├──────────────────┤
    │ • id (PK)          │  │ • id (PK)    │  │ • id (PK)        │
    │ • product_id (FK)  │  │ • product_id │  │ • product_id(FK) │
    │ • image            │  │   (FK)       │  │ • user_id (FK)   │
    │ • alt_text         │  │ • size       │  │ • rating         │
    │ • created_at       │  │ • color      │  │ • title          │
    └────────────────────┘  │ • quantity   │  │ • comment        │
                            │ • price      │  │ • created_at     │
                            │ • sku        │  │ • updated_at     │
                            │ • created_at │  └──────────────────┘
                            └──────────────┘

    ┌──────────────────────┐
    │     WISHLIST         │
    ├──────────────────────┤
    │ • id (PK)            │
    │ • user_id (FK)       │
    │ • product_id (FK)    │
    │ • created_at         │
    └──────────────────────┘
         M:N Junction Table

                              ┌──────────────────┐
                              │      CART        │
                              ├──────────────────┤
                              │ • id (PK)        │
                              │ • user_id (FK)   │
                              │ • session_id     │
                              │ • total_price    │
                              │ • created_at     │
                              │ • updated_at     │
                              └────────┬─────────┘
                                       │
                                       │ 1:N
                                       │
                            ┌──────────▼──────────┐
                            │    CART_ITEM        │
                            ├─────────────────────┤
                            │ • id (PK)           │
                            │ • cart_id (FK)      │
                            │ • product_id (FK)   │
                            │ • variant_id (FK)   │
                            │ • quantity          │
                            │ • price             │
                            │ • created_at        │
                            │ • updated_at        │
                            └─────────────────────┘

                              ┌──────────────────┐
                              │      ORDER       │
                              ├──────────────────┤
                              │ • id (PK)        │
                              │ • user_id (FK)   │
                              │ • status         │
                              │ • total_price    │
                              │ • tax_price      │
                              │ • shipping_cost  │
                              │ • payment_method │
                              │ • created_at     │
                              │ • updated_at     │
                              └────────┬─────────┘
                                       │
                ┌──────────────────────┼──────────────────────┐
                │                      │                      │
        ┌───────▼───────┐      ┌──────▼──────┐      ┌────────▼────────┐
        │  ORDER_ITEM   │      │   PAYMENT   │      │ ORDER_STATUS    │
        ├───────────────┤      ├─────────────┤      ├─────────────────┤
        │ • id (PK)     │      │ • id (PK)   │      │ • id (PK)       │
        │ • order_id    │      │ • order_id  │      │ • order_id (FK) │
        │   (FK)        │      │   (FK)      │      │ • status        │
        │ • product_id  │      │ • amount    │      │ • timestamp     │
        │   (FK)        │      │ • currency  │      │ • notes         │
        │ • variant_id  │      │ • stripe_id │      └─────────────────┘
        │   (FK)        │      │ • status    │
        │ • quantity    │      │ • created_at│
        │ • price       │      └─────────────┘
        └───────────────┘

                         ┌───────────────────┐
                         │  NOTIFICATION     │
                         ├───────────────────┤
                         │ • id (PK)         │
                         │ • user_id (FK)    │
                         │ • order_id (FK)   │
                         │ • type            │
                         │ • subject         │
                         │ • message         │
                         │ • is_sent         │
                         │ • created_at      │
                         └───────────────────┘
```

---

## Detailed Entity Definitions

### 1. **USER** (Custom User Model)
- **Primary Key**: id (UUID)
- **Attributes**:
  - email (unique, indexed)
  - username (unique)
  - first_name
  - last_name
  - password (hashed)
  - is_active (boolean)
  - is_staff (boolean)
  - created_at (timestamp)
  - updated_at (timestamp)
- **Relationships**:
  - 1:N with ADDRESS
  - 1:N with EMAIL_VERIFY
  - 1:N with PASSWORD_RESET
  - 1:N with CART
  - 1:N with ORDER
  - 1:N with REVIEW
  - 1:N with WISHLIST
  - 1:N with NOTIFICATION

---

### 2. **ADDRESS**
- **Primary Key**: id (UUID)
- **Foreign Key**: user_id (USER)
- **Attributes**:
  - street
  - city
  - state/province
  - zip_code
  - country
  - is_default (boolean)
  - created_at
  - updated_at
- **Purpose**: Store multiple delivery/billing addresses per user

---

### 3. **EMAIL_VERIFY** (Email Verification Token)
- **Primary Key**: id (UUID)
- **Foreign Key**: user_id (USER)
- **Attributes**:
  - token (unique)
  - created_at
  - expires_at
- **Purpose**: Store verification tokens for email confirmation

---

### 4. **PASSWORD_RESET** (Password Reset Token)
- **Primary Key**: id (UUID)
- **Foreign Key**: user_id (USER)
- **Attributes**:
  - token (unique)
  - created_at
  - expires_at
- **Purpose**: Store reset tokens for password recovery

---

### 5. **CATEGORY**
- **Primary Key**: id (UUID)
- **Attributes**:
  - name (indexed)
  - slug (unique, indexed)
  - description
  - image
  - is_active (boolean)
  - created_at
  - updated_at
- **Relationships**:
  - 1:N with PRODUCT
- **Purpose**: Organize products into categories

---

### 6. **PRODUCT**
- **Primary Key**: id (UUID)
- **Foreign Key**: category_id (CATEGORY)
- **Attributes**:
  - name (indexed)
  - slug (unique, indexed)
  - description
  - price (decimal, indexed)
  - sku (unique, indexed)
  - quantity (integer, indexed for low-stock alerts)
  - is_featured (boolean, indexed)
  - is_active (boolean, indexed)
  - created_at (indexed)
  - updated_at
- **Relationships**:
  - 1:N with PRODUCT_IMAGE
  - 1:N with VARIANT
  - 1:N with REVIEW
  - M:N with WISHLIST (through junction table)
  - 1:N with CART_ITEM
  - 1:N with ORDER_ITEM
- **Indexes**: Composite on (category_id, is_active), (name, created_at), (price, is_active)

---

### 7. **PRODUCT_IMAGE**
- **Primary Key**: id (UUID)
- **Foreign Key**: product_id (PRODUCT)
- **Attributes**:
  - image (file path)
  - alt_text
  - created_at
- **Purpose**: Store multiple images per product

---

### 8. **VARIANT** (Product Variant)
- **Primary Key**: id (UUID)
- **Foreign Key**: product_id (PRODUCT)
- **Attributes**:
  - size (e.g., S, M, L, XL)
  - color
  - quantity (stock for this variant)
  - price (variant-specific price)
  - sku (unique)
  - created_at
  - updated_at
- **Purpose**: Handle product variations (size, color combinations)

---

### 9. **REVIEW** (Product Review)
- **Primary Key**: id (UUID)
- **Foreign Keys**: 
  - product_id (PRODUCT)
  - user_id (USER)
- **Attributes**:
  - rating (1-5 integer)
  - title
  - comment (text)
  - created_at (indexed)
  - updated_at
- **Purpose**: Customer reviews and ratings

---

### 10. **WISHLIST** (User Wishlist)
- **Primary Key**: id (UUID)
- **Foreign Keys**:
  - user_id (USER)
  - product_id (PRODUCT)
- **Attributes**:
  - created_at
- **Type**: M:N junction table
- **Unique Constraint**: (user_id, product_id)
- **Purpose**: Track products users want to save

---

### 11. **CART** (Shopping Cart)
- **Primary Key**: id (UUID)
- **Foreign Key**: user_id (USER, nullable for guest carts)
- **Attributes**:
  - session_id (for guest carts)
  - total_price (denormalized, updated when items change)
  - created_at
  - updated_at
- **Relationships**:
  - 1:N with CART_ITEM
- **Purpose**: Session/user shopping cart

---

### 12. **CART_ITEM** (Cart Item)
- **Primary Key**: id (UUID)
- **Foreign Keys**:
  - cart_id (CART)
  - product_id (PRODUCT)
  - variant_id (VARIANT, nullable)
- **Attributes**:
  - quantity (integer)
  - price (snapshot of product price at add time)
  - created_at
  - updated_at
- **Purpose**: Individual items in a shopping cart

---

### 13. **ORDER** (Customer Order)
- **Primary Key**: id (UUID)
- **Foreign Key**: user_id (USER)
- **Attributes**:
  - status (choices: pending, processing, shipped, delivered, cancelled)
  - total_price (decimal)
  - tax_price (decimal)
  - shipping_cost (decimal)
  - payment_method (card, paypal, etc.)
  - created_at (indexed)
  - updated_at
- **Relationships**:
  - 1:N with ORDER_ITEM
  - 1:1 with PAYMENT
  - 1:N with ORDER_STATUS (history)
  - 1:N with NOTIFICATION
- **Indexes**: Composite on (user_id, created_at), (status, created_at)

---

### 14. **ORDER_ITEM** (Item in Order)
- **Primary Key**: id (UUID)
- **Foreign Keys**:
  - order_id (ORDER)
  - product_id (PRODUCT)
  - variant_id (VARIANT, nullable)
- **Attributes**:
  - quantity (integer)
  - price (snapshot at purchase time)
  - created_at
- **Purpose**: Track individual products in an order

---

### 15. **PAYMENT** (Payment Record)
- **Primary Key**: id (UUID)
- **Foreign Key**: order_id (ORDER)
- **Attributes**:
  - amount (decimal)
  - currency (e.g., USD)
  - stripe_id (external payment ID)
  - status (succeeded, failed, pending)
  - created_at
  - updated_at
- **Purpose**: Track payment transactions

---

### 16. **ORDER_STATUS** (Order Status History)
- **Primary Key**: id (UUID)
- **Foreign Key**: order_id (ORDER)
- **Attributes**:
  - status (from choices)
  - timestamp
  - notes (optional)
- **Purpose**: Audit trail of order status changes

---

### 17. **NOTIFICATION** (User Notification)
- **Primary Key**: id (UUID)
- **Foreign Keys**:
  - user_id (USER)
  - order_id (ORDER, nullable)
- **Attributes**:
  - type (order_confirmation, shipping_update, etc.)
  - subject
  - message
  - is_sent (boolean)
  - created_at
- **Purpose**: Track email/notification sending

---

## Relationships Summary

| From Entity | To Entity | Type | Cardinality |
|------------|-----------|------|------------|
| USER | ADDRESS | One-to-Many | 1:N |
| USER | EMAIL_VERIFY | One-to-Many | 1:N |
| USER | PASSWORD_RESET | One-to-Many | 1:N |
| USER | CART | One-to-Many | 1:N |
| USER | ORDER | One-to-Many | 1:N |
| USER | REVIEW | One-to-Many | 1:N |
| USER | WISHLIST | One-to-Many | 1:N |
| USER | NOTIFICATION | One-to-Many | 1:N |
| CATEGORY | PRODUCT | One-to-Many | 1:N |
| PRODUCT | PRODUCT_IMAGE | One-to-Many | 1:N |
| PRODUCT | VARIANT | One-to-Many | 1:N |
| PRODUCT | REVIEW | One-to-Many | 1:N |
| PRODUCT | WISHLIST | One-to-Many | 1:N |
| PRODUCT | CART_ITEM | One-to-Many | 1:N |
| PRODUCT | ORDER_ITEM | One-to-Many | 1:N |
| VARIANT | CART_ITEM | One-to-Many | 1:N |
| VARIANT | ORDER_ITEM | One-to-Many | 1:N |
| CART | CART_ITEM | One-to-Many | 1:N |
| ORDER | ORDER_ITEM | One-to-Many | 1:N |
| ORDER | PAYMENT | One-to-One | 1:1 |
| ORDER | ORDER_STATUS | One-to-Many | 1:N |
| ORDER | NOTIFICATION | One-to-Many | 1:N |

---

## Key Design Decisions

### 1. **UUID Primary Keys**
- All entities use UUID instead of auto-increment integers
- Better for distributed systems and privacy

### 2. **Denormalization**
- `PRODUCT.quantity`: Denormalized from VARIANT for quick stock checks
- `CART.total_price`: Calculated and stored for performance
- `ORDER.total_price`: Snapshot of prices at purchase time

### 3. **Indexing Strategy**
- **High-cardinality fields**: price, quantity, created_at
- **Composite indexes**: (category_id, is_active), (user_id, created_at)
- **Unique constraints**: email, username, slug, SKU

### 4. **Nullable Foreign Keys**
- `CART.user_id`: Nullable for guest carts (uses session_id)
- `VARIANT_ID` in CART_ITEM/ORDER_ITEM: Nullable for simple products

### 5. **Status as Choice Field**
- ORDER.status: Stored as string with predefined choices
- Indexed for efficient filtering by status

### 6. **Soft Delete Pattern**
- `is_active` flag used instead of actual deletion
- Preserves referential integrity and historical data

### 7. **Audit Trail**
- `created_at`, `updated_at` on all entities
- ORDER_STATUS maintains complete history

---

## Query Optimization Considerations

### Common Query Patterns:
1. **Product listing with category filter**
   - Index: (category_id, is_active, created_at)

2. **User orders**
   - Index: (user_id, created_at DESC)

3. **Cart items for checkout**
   - Index: (cart_id, created_at)

4. **Low stock products**
   - Index: (quantity, is_active)

5. **Product reviews**
   - Index: (product_id, created_at DESC)

---

## Database Constraints

### Unique Constraints:
- USER (email, username)
- CATEGORY (slug)
- PRODUCT (slug, sku)
- VARIANT (sku)
- WISHLIST (user_id, product_id)

### Not Null Constraints:
- All required fields marked as NOT NULL
- Foreign keys NOT NULL except where specified (nullable FKs)

### Check Constraints:
- REVIEW.rating: 1-5
- ORDER.total_price, tax_price, shipping_cost ≥ 0
- PRODUCT.price ≥ 0
