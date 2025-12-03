# Running the E-Commerce Backend

## Current Status

Docker is not installed on your system, but you have two options to run the application:

---

## Option 1: Development Server (Recommended - Already Configured)

The Django development server is perfect for testing and development.

### Start the Server

```bash
cd c:\Users\ALSAINT\Desktop\alx-project-nexus\e-commerce
python manage.py runserver 127.0.0.1:8000
```

### Access the Application

- **Swagger API Docs:** http://127.0.0.1:8000/api/docs/
- **Django Admin:** http://127.0.0.1:8000/admin/
- **API Base:** http://127.0.0.1:8000/api/v1/

### Admin Credentials
- **Username:** admin
- **Password:** password123

### Database

- Using **SQLite** (db.sqlite3) - Already seeded with sample data
- 11 categories, 9 products, 3 users, 2 orders, 18 reviews

### Features Available

✅ All 40+ REST endpoints
✅ Advanced filtering, sorting, pagination
✅ JWT authentication
✅ Email verification system
✅ Password reset functionality
✅ Shopping cart & orders
✅ Auto-generated API documentation
✅ Database seeded with sample data

---

## Option 2: Docker (Production-Ready)

For production-like environment with PostgreSQL, Redis, RabbitMQ, Celery.

### Prerequisites

1. **Install Docker Desktop** from: https://www.docker.com/products/docker-desktop

2. **Verify Installation**
```bash
docker --version
docker-compose --version
```

3. **Run Docker Compose**
```bash
cd c:\Users\ALSAINT\Desktop\alx-project-nexus\e-commerce
docker-compose up -d
```

### Services Included

- **Web:** Django with Gunicorn (port 8000)
- **Database:** PostgreSQL 15 (port 5432)
- **Cache:** Redis (port 6379)
- **Message Broker:** RabbitMQ (port 5672, admin: 15672)
- **Task Queue:** Celery workers
- **Scheduler:** Celery Beat
- **Reverse Proxy:** Nginx (port 80)

### Docker Access

```bash
# View running containers
docker ps

# View logs
docker logs ecommerce_web

# Execute Django commands
docker exec ecommerce_web python manage.py createsuperuser

# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Recommended Setup

### For Development/Testing
**Use Option 1 (Development Server)**
- Simpler to set up
- Faster iteration
- Perfect for testing all features
- SQLite database included with sample data

### For Production/Deployment
**Use Option 2 (Docker)**
- PostgreSQL for better performance
- Redis caching
- RabbitMQ for async tasks
- Celery for background jobs
- Nginx reverse proxy
- Container isolation

---

## Quick Start Commands

### Development Server

```bash
# Navigate to project
cd c:\Users\ALSAINT\Desktop\alx-project-nexus\e-commerce

# Activate virtual environment (if needed)
.\.venv\Scripts\Activate.ps1

# Start server
python manage.py runserver 127.0.0.1:8000

# Access at: http://127.0.0.1:8000/api/docs/
```

### Docker Setup

```bash
# Navigate to project
cd c:\Users\ALSAINT\Desktop\alx-project-nexus\e-commerce

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f web

# Access at: http://localhost:8000/api/docs/

# Stop services
docker-compose down
```

---

## Environment Configuration

### Development (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
```

### Docker (docker-compose.yml)
```
PostgreSQL: db
Redis: redis:6379
RabbitMQ: rabbitmq:5672
Django: web:8000
```

---

## API Testing Examples

### Using cURL

```bash
# Register
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# List products
curl http://127.0.0.1:8000/api/v1/products/

# Filter products
curl "http://127.0.0.1:8000/api/v1/products/?price_max=500&search=laptop"
```

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'config'"
**Solution:** Ensure you're in the correct directory
```bash
cd c:\Users\ALSAINT\Desktop\alx-project-nexus\e-commerce
```

### Issue: "Port 8000 already in use"
**Solution:** Use a different port
```bash
python manage.py runserver 127.0.0.1:8001
```

### Issue: "Database connection error"
**Solution:** Check database exists (SQLite should auto-create)
```bash
python manage.py migrate
```

### Issue: "Docker daemon not running"
**Solution:** Start Docker Desktop application

---

## Next Steps

1. **Choose your setup** (Development or Docker)
2. **Start the server** using appropriate command
3. **Access API docs** at http://127.0.0.1:8000/api/docs/
4. **Test endpoints** using Swagger UI or cURL
5. **Review documentation** (SUBMISSION_REPORT.md, etc.)

---

## Support

For detailed information:
- **API Reference:** http://127.0.0.1:8000/api/docs/
- **Documentation:** See README_COMPLETE.md
- **Admin Panel:** http://127.0.0.1:8000/admin/

---

**Your project is ready to run! Choose your preferred setup and start developing.** 🚀
