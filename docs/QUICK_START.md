# Quick Start Guide - E-Commerce Backend

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Docker & Docker Compose installed
- Git installed
- Basic knowledge of Django/REST APIs

### Quick Setup

```bash
# 1. Navigate to project directory
cd alx-project-nexus/e-commerce

# 2. Copy environment file
cp .env.example .env

# 3. Build and start Docker services
docker-compose up -d

# 4. Run migrations
docker-compose exec web python manage.py migrate

# 5. Create superuser
docker-compose exec web python manage.py createsuperuser

# 6. Access the application
# API: http://localhost:8000/api/v1/
# Admin: http://localhost:8000/admin/
```

## 🔧 Configuration

### Essential Environment Variables (.env)
```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
POSTGRES_PASSWORD=your-secure-password
STRIPE_SECRET_KEY=sk_test_your_key
EMAIL_HOST_PASSWORD=your-email-password
```

## 📚 API Usage Examples

### 1. User Registration
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 2. User Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### 3. List Products
```bash
curl http://localhost:8000/api/v1/products/?page=1&search=laptop
```

### 4. Add to Cart
```bash
curl -X POST http://localhost:8000/api/v1/cart/items/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "123e4567-e89b-12d3-a456-426614174000",
    "quantity": 1
  }'
```

### 5. Create Order (Checkout)
```bash
curl -X POST http://localhost:8000/api/v1/orders/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "shipping_address_id": "address-id",
    "billing_address_id": "address-id"
  }'
```

## 🛠 Common Commands

### Docker Commands
```bash
# View logs
docker-compose logs -f web

# Execute Django commands
docker-compose exec web python manage.py <command>

# Stop services
docker-compose down

# Remove volumes (reset data)
docker-compose down -v

# Restart services
docker-compose restart
```

### Django Management Commands
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Create test data
python manage.py seed_database

# Shell
python manage.py shell
```

### Celery Commands
```bash
# Start worker
celery -A config worker -l info

# Start beat scheduler
celery -A config beat -l info

# Inspect active tasks
celery -A config inspect active
```

## 📦 Services Running

- **Django App**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **RabbitMQ**: http://localhost:15672 (guest/guest)
- **Nginx**: http://localhost:80

## 🔑 Admin Access

1. Go to http://localhost:8000/admin/
2. Login with superuser credentials
3. Manage all entities through admin panel

## 📊 Database Backup

```bash
# Backup
docker-compose exec db pg_dump -U postgres ecommerce > backup.sql

# Restore
docker-compose exec -T db psql -U postgres ecommerce < backup.sql
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test
pytest apps/users/tests/test_views.py

# With coverage
pytest --cov=apps --cov-report=html
```

## 🐛 Troubleshooting

### Issue: Container failed to start
```bash
# Check logs
docker-compose logs web

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Database connection error
```bash
# Ensure PostgreSQL is healthy
docker-compose ps

# Reset database
docker-compose down -v
docker-compose up -d
```

### Issue: Permission denied errors
```bash
# Fix permissions
sudo chown -R $USER:$USER .
```

## 📖 Documentation Files

- `README.md` - Main project documentation
- `IMPLEMENTATION_SUMMARY.md` - Detailed implementation summary
- `API_DOCUMENTATION.md` - API endpoint reference
- `DEPLOYMENT.md` - Production deployment guide

## 🎓 Learning Resources

- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Celery: https://docs.celeryproject.org/
- PostgreSQL: https://www.postgresql.org/docs/

## 💡 Pro Tips

1. **Use Django Shell**: `python manage.py shell` for quick queries
2. **Monitor Celery**: Open http://localhost:5555 (if Flower installed)
3. **API Testing**: Use Postman or httpie for testing
4. **Admin Site**: The Django admin is your best friend for data management

## 🚀 Next Steps

1. Load sample data: `python manage.py seed_database`
2. Test API endpoints
3. Build frontend integration
4. Configure email settings for production
5. Set up payment processor (Stripe) credentials

## 📞 Support

For issues or questions:
1. Check the documentation
2. Review error logs
3. Check Django admin
4. Inspect database directly

## 🎯 Development Workflow

```
1. Create feature branch
2. Make changes
3. Run tests: pytest
4. Format code: black .
5. Commit changes
6. Push to GitHub
7. Create Pull Request
```

---

**Happy Coding! 🚀**

For detailed information, see the main README.md file.
