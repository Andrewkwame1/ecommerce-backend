# E-commerce Backend API

A robust, scalable e-commerce backend built with Django REST Framework, featuring JWT authentication, asynchronous task processing, caching, and comprehensive API endpoints.

## 🚀 Features

- **User Management**: Registration, authentication, email verification, password reset
- **Product Catalog**: Categories, products, variants, reviews, wishlist
- **Shopping Cart**: Session-based and user-based carts
- **Order Management**: Checkout, order tracking, status updates
- **Payment Integration**: Stripe payment processing
- **Asynchronous Tasks**: Email notifications, inventory updates via Celery
- **Caching**: Redis caching for improved performance
- **API Documentation**: RESTful API with filtering, search, and pagination

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- RabbitMQ 3+

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ecommerce-backend.git
cd ecommerce-backend
```

### 2. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=ecommerce
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

STRIPE_SECRET_KEY=sk_test_your_stripe_key
```

### 3. Using Docker (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load seed data (optional)
docker-compose exec web python manage.py loaddata seed_data.json
```

The API will be available at `http://localhost:8000`

### 4. Manual Setup (Without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# In separate terminals, start Celery
celery -A config worker -l info
celery -A config beat -l info
```

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register/` | Register new user |
| POST | `/api/v1/auth/login/` | Login user |
| POST | `/api/v1/auth/logout/` | Logout user |
| POST | `/api/v1/auth/refresh/` | Refresh access token |
| GET | `/api/v1/auth/verify-email/<token>/` | Verify email |
| POST | `/api/v1/auth/password/reset/` | Request password reset |
| POST | `/api/v1/auth/password/reset/confirm/` | Confirm password reset |
| POST | `/api/v1/auth/password/change/` | Change password |

### User Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/auth/me/` | Get user profile |
| PUT | `/api/v1/auth/me/` | Update user profile |
| GET | `/api/v1/auth/me/addresses/` | List user addresses |
| POST | `/api/v1/auth/me/addresses/` | Create address |
| PUT | `/api/v1/auth/me/addresses/<id>/` | Update address |
| DELETE | `/api/v1/auth/me/addresses/<id>/` | Delete address |

### Product Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/products/` | List products |
| GET | `/api/v1/products/<slug>/` | Get product details |
| GET | `/api/v1/products/<slug>/reviews/` | List product reviews |
| POST | `/api/v1/products/<slug>/reviews/` | Create review |
| GET | `/api/v1/products/categories/` | List categories |
| POST | `/api/v1/products/<slug>/wishlist/` | Toggle wishlist |
| GET | `/api/v1/products/wishlist/me/` | Get user wishlist |

### Cart Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/cart/` | Get cart |
| POST | `/api/v1/cart/items/` | Add to cart |
| PUT | `/api/v1/cart/items/<id>/` | Update cart item |
| DELETE | `/api/v1/cart/items/<id>/` | Remove from cart |
| DELETE | `/api/v1/cart/clear/` | Clear cart |

### Order Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/orders/` | List user orders |
| POST | `/api/v1/orders/` | Create order (checkout) |
| GET | `/api/v1/orders/<id>/` | Get order details |
| POST | `/api/v1/orders/<id>/cancel/` | Cancel order |

### Payment Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/payments/create-intent/` | Create payment intent |
| POST | `/api/v1/payments/confirm/` | Confirm payment |
| POST | `/api/v1/payments/webhook/` | Stripe webhook |

## 🔍 Query Parameters

### Product List Filters

```
GET /api/v1/products/?category=electronics&min_price=100&max_price=500&in_stock=true&featured=true&search=laptop&ordering=-created_at&page=1
```

**Available filters:**
- `category` - Filter by category slug
- `min_price` - Minimum price
- `max_price` - Maximum price
- `in_stock` - Show only in-stock items
- `featured` - Show only featured products
- `search` - Search in name, description, SKU
- `ordering` - Sort by: `price`, `-price`, `created_at`, `-created_at`, `name`
- `page` - Page number

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Run specific app tests
python manage.py test apps.users
python manage.py test apps.products
```

## 📊 Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View migration status
python manage.py showmigrations

# Revert migration
python manage.py migrate app_name migration_name
```

## 🔧 Management Commands

### Seed Database

```bash
python manage.py loaddata seed_data.json
```

### Create Sample Data

```python
# scripts/seed_data.py
from apps.users.models import User
from apps.products.models import Category, Product

# Create categories
electronics = Category.objects.create(name="Electronics", slug="electronics")
clothing = Category.objects.create(name="Clothing", slug="clothing")

# Create products
Product.objects.create(
    name="Laptop",
    slug="laptop",
    description="High-performance laptop",
    category=electronics,
    price=999.99,
    sku="LAP-001",
    quantity=50
)
```

## 📈 Performance Optimization

### Caching Strategy

```python
# Cache product list for 1 hour
cache.set('products_list', products, 3600)

# Cache product detail for 5 minutes
cache.set(f'product_detail_{slug}', data, 300)
```

### Query Optimization

```python
# Use select_related for foreign keys
products = Product.objects.select_related('category').all()

# Use prefetch_related for many-to-many
products = Product.objects.prefetch_related('images', 'reviews').all()
```

## 🚢 Deployment

### Production Settings

Update `config/settings/production.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Static files on S3
USE_S3 = True
```

### Deploy with Docker

```bash
# Build production image
docker build -t ecommerce-backend:latest .

# Run migrations
docker-compose -f docker-compose.prod.yml run web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml run web python manage.py collectstatic --noinput

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit `.env` file
2. **JWT Tokens**: Short-lived access tokens (1 hour), longer refresh tokens (7 days)
3. **Rate Limiting**: Implemented on authentication endpoints
4. **Input Validation**: All user inputs are validated
5. **SQL Injection**: Django ORM prevents SQL injection
6. **XSS Protection**: Django templates auto-escape by default
7. **CORS**: Configured for specific domains only

## 📝 Project Structure Explanation

```
ecommerce-backend/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
├── # E-Commerce Backend API

A comprehensive, production-ready Django REST Framework e-commerce backend with complete API implementation.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Database](#database)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

## ✨ Features

### Core Features
- **User Management**: Registration, authentication, profile management, address management
- **Product Catalog**: Full product CRUD, categories, variants, search, filtering
- **Shopping Cart**: Add/remove/update items, guest cart support, persistent storage
- **Order Management**: Complete order lifecycle, status tracking, order history
- **Payment Integration**: Stripe payment processing with webhook support
- **Wishlist**: User wishlists with add/remove functionality
- **Reviews**: Product reviews with ratings and verification

### Advanced Features
- **Asynchronous Tasks**: Celery with RabbitMQ for background jobs
- **Email Notifications**: Order confirmations, shipping updates, password resets
- **Caching Strategy**: Redis caching for products and sessions
- **Inventory Management**: Stock tracking, low-stock alerts
- **Admin Dashboard**: Comprehensive admin panel (Django admin)

### Security & Performance
- **JWT Authentication**: Secure token-based authentication
- **Rate Limiting**: API rate limiting to prevent abuse
- **CORS Support**: Configurable CORS for multiple frontends
- **Data Validation**: Comprehensive input validation
- **Query Optimization**: select_related and prefetch_related usage
- **Pagination**: Efficient pagination for large datasets
- **Monitoring**: Sentry integration for error tracking
- **Logging**: Comprehensive application logging

## 🛠 Tech Stack

**Backend:**
- Python 3.11+
- Django 5.0+
- Django REST Framework 3.15+
- PostgreSQL 15
- Redis 7
- Celery 5.3+
- RabbitMQ 3

**DevOps:**
- Docker & Docker Compose
- Nginx (reverse proxy)
- Gunicorn (WSGI server)
- GitHub Actions (CI/CD)

**Additional:**
- Stripe API
- AWS S3 (optional)
- Sentry (error tracking)

## 📁 Project Structure

```
ecommerce/
├── config/                      # Project configuration
│   ├── settings/
│   │   ├── base.py             # Base settings
│   │   ├── development.py      # Dev settings
│   │   ├── production.py       # Prod settings
│   │   └── test.py             # Test settings
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
│
├── apps/                        # Django apps
│   ├── users/                  # User management
│   ├── products/               # Product catalog
│   ├── cart/                   # Shopping cart
│   ├── orders/                 # Order management
│   ├── payments/               # Payment processing
│   └── notifications/          # Notifications
│
├── utils/                       # Shared utilities
│   ├── exceptions.py
│   ├── pagination.py
│   ├── permissions.py
│   └── validators.py
│
├── static/                      # Static files
├── media/                       # User uploads
├── logs/                        # Application logs
├── scripts/                     # Management scripts
├── templates/                   # Email templates
│
├── docker-compose.yml           # Docker compose config
├── Dockerfile                   # Docker image
├── nginx.conf                   # Nginx configuration
├── requirements.txt             # Python dependencies
└── manage.py                    # Django management
```

## 🚀 Installation

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Git

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ecommerce-backend.git
   cd ecommerce-backend
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build Docker images**
   ```bash
   docker-compose build
   ```

4. **Start services**
   ```bash
   docker-compose up -d
   ```

5. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

7. **Access the application**
   - API: http://localhost:8000/api/v1/
   - Admin: http://localhost:8000/admin/
   - RabbitMQ: http://localhost:15672/ (guest/guest)

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with your configuration.

## 🏃 Running the Application

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

### Local Development

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Start Celery worker (in another terminal)
celery -A config worker -l info
```

## 📚 API Documentation

See `API_DOCUMENTATION.md` for detailed endpoint documentation.

## 🗄️ Database

### Models Overview

**Users App:**
- User (custom user model)
- UserProfile
- Address
- EmailVerificationToken
- PasswordResetToken

**Products App:**
- Category
- Product
- ProductImage
- ProductVariant
- Review
- Wishlist

**Cart App:**
- Cart
- CartItem

**Orders App:**
- Order
- OrderItem
- OrderStatusHistory

**Payments App:**
- Payment

**Notifications App:**
- Notification

### Migrations

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=apps --cov-report=html

# Run specific test
pytest apps/users/tests/test_views.py
```

## 🚀 Deployment

For production deployment guidelines, see `DEPLOYMENT.md`.

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

**Last Updated:** December 2025
├── manage.py
│
├── config/                      # Project settings
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py             # Base settings
│   │   ├── development.py      # Dev settings
│   │   ├── production.py       # Prod settings
│   │   └── test.py             # Test settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                        # Django apps
│   ├── users/                  # User management
│   │   ├── migrations/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── permissions.py
│   │   ├── tasks.py           # Celery tasks
│   │   └── tests/
│   │
│   ├── products/               # Product catalog
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── filters.py
│   │   ├── tasks.py
│   │   └── tests/
│   │
│   ├── cart/                   # Shopping cart
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   ├── orders/                 # Order management
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tasks.py
│   │   └── tests/
│   │
│   ├── payments/               # Payment processing
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── services.py        # Payment gateway logic
│   │   └── tests/
│   │
│   └── notifications/          # Email/SMS notifications
│       ├── models.py
│       ├── tasks.py
│       ├── services.py
│       └── tests/
│
├── utils/                       # Shared utilities
│   ├── __init__.py
│   ├── exceptions.py
│   ├── validators.py
│   ├── pagination.py
│   └── permissions.py
│
├── static/                      # Static files
├── media/                       # User uploads
├── logs/                        # Application logs
│
└── scripts/                     # Management scripts
    ├── seed_data.py
    └── backup_db.sh
```

## 📄 License

This project is licensed under the MIT License.

## 👥 Contact

Your Name - your.email@example.com

Project Link: https://github.com/yourusername/ecommerce-backend

## 🙏 Acknowledgments

- Django REST Framework
- Celery
- Stripe
- PostgreSQL
- Redis
- RabbitMQ