# E-Commerce Backend API

A production-ready, scalable e-commerce backend built with **Django REST Framework 3.16**, featuring JWT authentication, asynchronous task processing, comprehensive testing, and enterprise-grade security.

## 🎯 Project Status

[![Deployment Status](https://img.shields.io/badge/Deployment-Live-brightgreen?style=flat-square&logo=render)](https://ecommerce-backend-2-88ro.onrender.com)
[![Build Status](https://github.com/Andrewkwame1/ecommerce-backend/actions/workflows/deploy.yml/badge.svg)](https://github.com/Andrewkwame1/ecommerce-backend/actions/workflows/deploy.yml)
[![Tests](https://img.shields.io/badge/Tests-18/18%20Passing-brightgreen?style=flat-square)](https://github.com/Andrewkwame1/ecommerce-backend/actions)
[![Code Coverage](https://img.shields.io/badge/Coverage-~50%25-yellow?style=flat-square)](coverage.xml)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)](https://www.python.org/downloads/)
[![Django Version](https://img.shields.io/badge/Django-5.2.8-darkgreen?style=flat-square&logo=django)](https://www.djangoproject.com/)
[![DRF Version](https://img.shields.io/badge/DRF-3.16-red?style=flat-square)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

✅ **Production Ready** | 🔒 **Secure** | 📊 **Well-Tested** | 🚀 **Deployed**

- **Live API**: https://ecommerce-backend-2-88ro.onrender.com/api/v1/
- **Admin Dashboard**: https://ecommerce-backend-2-88ro.onrender.com/admin/
- **API Documentation**: https://ecommerce-backend-2-88ro.onrender.com/api/docs/
- **Schema**: https://ecommerce-backend-2-88ro.onrender.com/api/schema/

## ✨ Key Features

### Core E-Commerce
- **User Management**: Registration, authentication, profile management, address management
- **Product Catalog**: Full CRUD, categories, filtering, search, reviews, wishlist
- **Shopping Cart**: Add/remove/update items, session persistence
- **Order Management**: Complete lifecycle, status tracking, order history
- **Payment Integration**: Stripe integration with webhook support
- **Reviews & Ratings**: Product reviews with user verification

### Advanced Features
- **Asynchronous Tasks**: Celery + RabbitMQ for background jobs
- **Email Notifications**: Order confirmations, password resets, shipping updates
- **Caching Strategy**: Redis caching for products and sessions
- **Inventory Management**: Stock tracking and low-stock alerts
- **Admin Dashboard**: Comprehensive Django admin interface

### Security & Quality
- **JWT Authentication**: Secure token-based auth (access + refresh tokens)
- **Rate Limiting**: API rate limiting to prevent abuse
- **Comprehensive Testing**: 18 automated tests with coverage reporting
- **CORS Support**: Configurable cross-origin requests
- **Input Validation**: Full request validation with error handling
- **Type Hints**: 34+ type annotations for code clarity
- **Code Quality**: Zero warnings, clean code architecture

## 🚀 Quick Demo

### Test the Live API (No Setup Required!)

```bash
# Get API information
curl https://ecommerce-backend-2-88ro.onrender.com/api/v1/

# Check health status
curl https://ecommerce-backend-2-88ro.onrender.com/healthz/

# List products
curl https://ecommerce-backend-2-88ro.onrender.com/api/v1/products/

# View API documentation
# Open: https://ecommerce-backend-2-88ro.onrender.com/api/docs/
```

### Or Run Locally with Docker

```bash
# Clone & setup
git clone https://github.com/Andrewkwame1/ecommerce-backend.git
cd ecommerce-backend/e-commerce

# Build Docker image
docker build -t ecommerce-api:dev .

# Run container
docker run -d --name api -p 8000:8000 ecommerce-api:dev

# Access locally
# http://localhost:8000/api/v1/
# http://localhost:8000/api/docs/
```

## 📋 Prerequisites

- **Python 3.11+**
- **Docker & Docker Compose**
- **PostgreSQL 15+**
- **Redis 7+**
- **RabbitMQ 3+**

## 🛠️ Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/Andrewkwame1/ecommerce-backend.git
cd ecommerce-backend

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Build and start services
docker-compose up --build

# Run migrations (in another terminal)
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access the API
# http://localhost:8000/api/v1/
# http://localhost:8000/api/docs/
# http://localhost:8000/admin/
```

### Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env

# Run migrations
cd e-commerce
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver

# Start Celery (in separate terminals)
celery -A config worker -l info
celery -A config beat -l info
```

## 🌐 API Endpoints

### Base URL
```
Production: https://ecommerce-backend-2-88ro.onrender.com/api/v1/
Local Dev: http://localhost:8000/api/v1/
```

### Authentication Endpoints
```
POST   /api/v1/auth/register/           # Register new user
POST   /api/v1/auth/login/              # Login user
POST   /api/v1/auth/logout/             # Logout user
POST   /api/v1/auth/refresh/            # Refresh access token
GET    /api/v1/auth/verify-email/<token>/  # Verify email
POST   /api/v1/auth/password/reset/     # Request password reset
POST   /api/v1/auth/password/reset/confirm/ # Confirm password reset
```

### User Endpoints
```
GET    /api/v1/auth/me/                 # Get user profile
PUT    /api/v1/auth/me/                 # Update user profile
GET    /api/v1/auth/me/addresses/       # List user addresses
POST   /api/v1/auth/me/addresses/       # Create address
```

### Product Endpoints
```
GET    /api/v1/products/                # List products
GET    /api/v1/products/<slug>/         # Get product details
GET    /api/v1/products/<slug>/reviews/ # List product reviews
POST   /api/v1/products/<slug>/reviews/ # Create review
POST   /api/v1/products/<slug>/wishlist/ # Toggle wishlist
```

### Cart Endpoints
```
GET    /api/v1/cart/                    # Get cart
POST   /api/v1/cart/items/              # Add to cart
PUT    /api/v1/cart/items/<id>/         # Update cart item
DELETE /api/v1/cart/items/<id>/         # Remove from cart
DELETE /api/v1/cart/clear/              # Clear entire cart
```

### Order Endpoints
```
GET    /api/v1/orders/                  # List user orders
POST   /api/v1/orders/                  # Create order (checkout)
GET    /api/v1/orders/<id>/             # Get order details
POST   /api/v1/orders/<id>/cancel/      # Cancel order
```

### Payment Endpoints
```
POST   /api/v1/payments/create-intent/  # Create payment intent
POST   /api/v1/payments/confirm/        # Confirm payment
POST   /api/v1/payments/webhook/        # Stripe webhook
```

## 🔍 Query Parameters

### Product Filtering
```
GET /api/v1/products/?category=electronics&min_price=100&max_price=500&in_stock=true&search=laptop&ordering=-created_at&page=1
```

**Available filters:**
- `category` - Filter by category slug
- `min_price` / `max_price` - Price range filtering
- `in_stock` - Show only in-stock items (true/false)
- `featured` - Show only featured products
- `search` - Search in name, description, SKU
- `ordering` - Sort by: `price`, `-price`, `created_at`, `-created_at`, `name`
- `page` - Pagination page number

## 🧪 Testing

```bash
# Run all tests with coverage
pytest --cov=apps --cov-report=html --cov-report=term

# Run tests with JUnit XML output
pytest --junitxml=junit.xml -v

# Run specific test module
pytest apps/users/tests.py

# Run with verbose output
pytest -v

# Generate coverage report
coverage run --source='.' manage.py test
coverage report
coverage html
```

**Test Coverage:**
- ✅ 18 automated tests
- ✅ ~50% code coverage
- ✅ All core modules tested
- ✅ API endpoint validation
- ✅ Model integrity tests

## 📊 Database Models

### Users App
- `User` - Custom user model with email authentication
- `UserProfile` - Extended user information
- `Address` - User addresses for shipping

### Products App
- `Category` - Product categories
- `Product` - Core product model
- `ProductImage` - Product images
- `ProductVariant` - Product variants (size, color, etc.)
- `Review` - Product reviews with ratings
- `Wishlist` - User wishlists

### Cart App
- `Cart` - User shopping cart
- `CartItem` - Individual cart items

### Orders App
- `Order` - Customer orders
- `OrderItem` - Individual order items
- `OrderStatusHistory` - Order status tracking

### Payments App
- `Payment` - Payment records with Stripe integration

### Notifications App
- `Notification` - System notifications

## 🔐 Security Features

✅ **Implemented:**
- JWT authentication with access/refresh tokens
- Cryptographically secure SECRET_KEY generation
- SECURE_SSL_REDIRECT enabled in production
- Password hashing with Django's default algorithm
- CSRF protection
- Rate limiting on auth endpoints
- Input validation and sanitization
- SQL injection prevention (Django ORM)
- XSS protection (template auto-escaping)
- CORS configured for specific domains
- Environment variables for sensitive data
- No secrets in version control

## 🚀 Deployment

### Production Environment
- **Platform**: Render.com
- **Database**: PostgreSQL (managed)
- **Redis**: Managed Redis instance
- **Static Files**: Served via whitenoise
- **Media Files**: Local storage (can be configured for S3)

### Environment Configuration

Create `.env` file with:
```env
# Django
DJANGO_SECRET_KEY=<50+ character random key>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DB_NAME=ecommerce
DB_USER=postgres
DB_PASSWORD=<strong password>
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/1

# Celery
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-specific password>

# Stripe
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
```

### Docker Deployment

```bash
# Build production image
docker build -t ecommerce-backend:latest .

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Start services
docker-compose -f docker-compose.prod.yml up -d
```

## 📁 Project Structure

```
alx-project-nexus/
├── e-commerce/                          # Django application root
│   ├── config/                          # Project configuration
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── __init__.py
│   │   │   ├── base.py                 # Base settings (shared)
│   │   │   ├── development.py          # Development overrides
│   │   │   ├── production.py           # Production overrides
│   │   │   └── test.py                 # Test settings
│   │   ├── urls.py                     # URL routing configuration
│   │   ├── wsgi.py                     # WSGI application
│   │   ├── asgi.py                     # ASGI application
│   │   ├── celery.py                   # Celery configuration
│   │   └── health.py                   # Health check endpoints
│   │
│   ├── apps/                            # Django applications
│   │   ├── users/                      # User management app
│   │   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py                # Admin configuration
│   │   │   ├── apps.py
│   │   │   ├── models.py               # User models
│   │   │   ├── serializers.py          # REST serializers
│   │   │   ├── views.py                # API views
│   │   │   ├── urls.py                 # URL patterns
│   │   │   ├── permissions.py          # Custom permissions
│   │   │   ├── tasks.py                # Celery tasks
│   │   │   └── tests.py                # Unit tests (6 user + 3 API tests)
│   │   │
│   │   ├── products/                   # Product catalog app
│   │   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py                # Admin interface
│   │   │   ├── apps.py
│   │   │   ├── models.py               # Category, Product, Review, Wishlist
│   │   │   ├── serializers.py          # Product serializers
│   │   │   ├── views.py                # Product views
│   │   │   ├── urls.py                 # Product routes
│   │   │   ├── filters.py              # Search & filtering
│   │   │   ├── tasks.py                # Background tasks
│   │   │   └── tests.py                # Product tests
│   │   │
│   │   ├── cart/                       # Shopping cart app
│   │   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py               # Cart and CartItem models
│   │   │   ├── serializers.py          # Cart serializers
│   │   │   ├── views.py                # Cart API endpoints
│   │   │   ├── urls.py                 # Cart routes
│   │   │   └── tests.py                # Cart tests (3 tests)
│   │   │
│   │   ├── orders/                     # Order management app
│   │   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py                # Order admin
│   │   │   ├── apps.py
│   │   │   ├── models.py               # Order and OrderItem
│   │   │   ├── serializers.py          # Order serializers
│   │   │   ├── views.py                # Order API views
│   │   │   ├── urls.py                 # Order routes
│   │   │   ├── tasks.py                # Order processing tasks
│   │   │   └── tests.py                # Order tests (3 tests)
│   │   │
│   │   ├── payments/                   # Payment processing app
│   │   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py
│   │   │   ├── apps.py
│   │   │   ├── models.py               # Payment model
│   │   │   ├── serializers.py          # Payment serializers
│   │   │   ├── views.py                # Stripe integration views
│   │   │   ├── urls.py                 # Payment routes
│   │   │   ├── services.py             # Stripe service layer
│   │   │   └── tests.py                # Payment tests (3 tests)
│   │   │
│   │   └── notifications/              # Email notifications app
│   │       ├── migrations/
│   │       ├── __init__.py
│   │       ├── admin.py
│   │       ├── apps.py
│   │       ├── models.py               # Notification model
│   │       ├── tasks.py                # Email sending tasks
│   │       └── services.py             # Notification services
│   │
│   ├── utils/                           # Shared utilities
│   │   ├── __init__.py
│   │   ├── exceptions.py               # Custom exception classes
│   │   ├── validators.py               # Input validators
│   │   ├── pagination.py               # Pagination classes
│   │   ├── permissions.py              # Custom DRF permissions
│   │   ├── cache.py                    # Caching utilities
│   │   └── inventory.py                # Inventory management
│   │
│   ├── static/                          # Static files (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   ├── media/                           # User uploaded files
│   │   ├── products/
│   │   ├── avatars/
│   │   └── documents/
│   │
│   ├── logs/                            # Application logs
│   │   ├── debug.log
│   │   ├── error.log
│   │   └── access.log
│   │
│   ├── scripts/                         # Management scripts
│   │   ├── __init__.py
│   │   ├── seed_data.py                # Database seeding
│   │   └── cleanup.py                  # Cleanup tasks
│   │
│   ├── templates/                       # Email templates
│   │   └── emails/
│   │       ├── welcome.html
│   │       ├── order_confirmation.html
│   │       ├── password_reset.html
│   │       └── email_verification.html
│   │
│   ├── manage.py                        # Django management script
│   ├── conftest.py                      # Pytest configuration
│   ├── pytest.ini                       # Pytest settings
│   ├── docker-compose.yml               # Docker compose config
│   ├── Dockerfile                       # Docker image build
│   └── nginx.conf                       # Nginx configuration
│
├── .github/
│   └── workflows/
│       └── deploy.yml                   # GitHub Actions CI/CD
│
├── .env.example                         # Environment template
├── .gitignore                           # Git ignore rules
├── requirements.txt                     # Production dependencies
├── requirements-dev.txt                 # Development dependencies
├── README.md                            # This file
└── LICENSE                              # MIT License
```

## 📂 Key Directories Explained

### `config/`
Central configuration hub for Django settings based on environment (development/production/test).

### `apps/`
Six Django apps, each handling a specific domain:
- **users**: Authentication, profiles, addresses
- **products**: Catalog, reviews, wishlist
- **cart**: Shopping cart management
- **orders**: Order processing, tracking
- **payments**: Stripe integration
- **notifications**: Email notifications

### `utils/`
Shared utilities used across apps:
- Custom exceptions and validators
- Pagination and permissions
- Caching and inventory logic

### `static/` & `media/`
- `static/`: CSS, JavaScript, images (served by Whitenoise)
- `media/`: User uploads (products, avatars, documents)

### `templates/`
Email templates for notifications:
- Welcome emails
- Order confirmations
- Password reset emails
- Email verification

## 🔄 CI/CD Pipeline

**GitHub Actions Workflow:**
1. ✅ Validate Django settings
2. ✅ Run 18 automated tests
3. ✅ Generate code coverage reports (HTML, XML, Terminal)
4. ✅ Build Docker image
5. ✅ Push to Docker Hub
6. ✅ Deploy to Render.com

## 📦 Tech Stack

- **Framework**: Django 5.2.8 + DRF 3.16
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Task Queue**: Celery + RabbitMQ
- **Testing**: pytest + pytest-django + coverage
- **API Docs**: drf-spectacular (OpenAPI 3.0)
- **Authentication**: JWT (simplejwt)
- **Payment**: Stripe
- **Deployment**: Docker, Render.com

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

## 📝 License

Licensed under the **MIT License**

## 👤 Author

**Andrew Kwame** - [@Andrewkwame1](https://github.com/Andrewkwame1)

## 📞 Support

- 🐛 [GitHub Issues](https://github.com/Andrewkwame1/ecommerce-backend/issues)
- 🌐 [Live API](https://ecommerce-backend-2-88ro.onrender.com)

## 🙏 Acknowledgments

- Django & DRF community
- Stripe API
- PostgreSQL & Redis
- Celery team
- All contributors

---

**Last Updated:** December 2025 | **Status:** Production Ready ✅

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
