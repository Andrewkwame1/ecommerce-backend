# Docker Quick Start Script for E-Commerce Backend

## Steps to Get Docker Running

### 1️⃣ Install Docker Desktop

**Download from:** https://www.docker.com/products/docker-desktop

**Installation:**
1. Run the installer
2. Follow the setup wizard
3. Restart your computer
4. Open Docker Desktop application

**Verify:**
```powershell
docker --version
docker-compose --version
```

---

### 2️⃣ Create Environment File

In `c:\Users\ALSAINT\Desktop\alx-project-nexus\e-commerce\`, create `.env`:

```
DEBUG=False
SECRET_KEY=django-insecure-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,web

POSTGRES_DB=ecommerce_db
POSTGRES_USER=ecommerce_user
POSTGRES_PASSWORD=secure_password_123
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/0

CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/1

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

---

### 3️⃣ Navigate to Project

```powershell
cd c:\Users\ALSAINT\Desktop\alx-project-nexus\e-commerce
```

---

### 4️⃣ Build Docker Images

```powershell
docker-compose build
```

**Output:**
```
Building web...
Building celery...
Building celery-beat...
[+] Building 120.5s (15/15) FINISHED
```

---

### 5️⃣ Start Services

```powershell
docker-compose up -d
```

**Output:**
```
[+] Running 7/7
 ✓ ecommerce_db
 ✓ ecommerce_redis
 ✓ ecommerce_rabbitmq
 ✓ ecommerce_web
 ✓ ecommerce_celery
 ✓ ecommerce_celery_beat
 ✓ ecommerce_nginx
```

---

### 6️⃣ Check Services Status

```powershell
docker-compose ps
```

**Output should show all healthy:**
```
NAME                     STATUS              PORTS
ecommerce_db            Up (healthy)         5432/tcp
ecommerce_redis         Up (healthy)         6379/tcp
ecommerce_rabbitmq      Up (healthy)         5672/tcp, 15672/tcp
ecommerce_web           Up (healthy)         8000/tcp
ecommerce_celery        Up                   
ecommerce_celery_beat   Up                   
ecommerce_nginx         Up                   80/tcp, 443/tcp
```

---

### 7️⃣ Run Database Migrations

```powershell
docker-compose exec web python manage.py migrate
```

---

### 8️⃣ Create Superuser (Optional)

```powershell
docker-compose exec web python manage.py createsuperuser
```

Or use the existing admin user (already in database):
- Username: `admin`
- Password: `password123`

---

### 9️⃣ Access the Application

| Service | URL | Credentials |
|---------|-----|-------------|
| **API Docs** | http://localhost:8000/api/docs/ | N/A |
| **Admin Panel** | http://localhost:8000/admin/ | admin / password123 |
| **RabbitMQ** | http://localhost:15672/ | guest / guest |
| **API Base** | http://localhost:8000/api/v1/ | N/A |

---

## 🔍 Verify Everything Works

### Test API Endpoint

```powershell
curl http://localhost:8000/api/v1/products/
```

### Check Logs

```powershell
# Django logs
docker-compose logs -f web

# Celery logs
docker-compose logs -f celery

# All logs
docker-compose logs -f
```

### Database Check

```powershell
docker-compose exec db psql -U ecommerce_user -d ecommerce_db -c "\dt"
```

---

## 📊 Services Overview

### PostgreSQL Database
- **Status:** Check with `docker-compose ps`
- **Port:** 5432 (internal)
- **Credentials:** ecommerce_user / secure_password_123
- **Database:** ecommerce_db
- **Data:** Persisted in postgres_data volume

### Redis Cache
- **Status:** Check with `docker-compose ps`
- **Port:** 6379 (internal)
- **Usage:** Caching, session storage
- **Data:** Persisted in redis_data volume

### RabbitMQ Message Broker
- **Admin URL:** http://localhost:15672/
- **Username:** guest
- **Password:** guest
- **Ports:** 5672 (messaging), 15672 (admin)

### Django Web Application
- **URL:** http://localhost:8000/
- **API Docs:** http://localhost:8000/api/docs/
- **Admin:** http://localhost:8000/admin/
- **Server:** Gunicorn with 4 workers

### Celery Workers
- **Purpose:** Async task processing
- **Broker:** RabbitMQ
- **Result Backend:** Redis
- **Status:** Check logs with `docker-compose logs celery`

### Celery Beat Scheduler
- **Purpose:** Scheduled task execution
- **Scheduler:** Django database scheduler
- **Status:** Check logs with `docker-compose logs celery-beat`

### Nginx Reverse Proxy
- **HTTP Port:** 80
- **HTTPS Port:** 443
- **Purpose:** Load balancing, SSL termination
- **Upstream:** Django app on port 8000

---

## 🛑 Stop Services

```powershell
# Stop without removing
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes)
docker-compose down -v

# Stop specific service
docker-compose stop web
docker-compose stop celery
```

---

## 🔄 Restart Services

```powershell
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart web
docker-compose restart celery
docker-compose restart db

# Full restart (stop + start)
docker-compose down
docker-compose up -d
```

---

## 📝 Common Tasks

### View Logs

```powershell
# Last 100 lines
docker-compose logs --tail=100

# Follow logs in real-time
docker-compose logs -f

# Specific service logs
docker-compose logs -f web
docker-compose logs -f celery
docker-compose logs -f db
```

### Run Django Commands

```powershell
# Migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Admin creation
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Database shell
docker-compose exec web python manage.py dbshell

# Django shell
docker-compose exec web python manage.py shell
```

### Run Tests

```powershell
# All tests
docker-compose exec web pytest

# With coverage
docker-compose exec web pytest --cov=apps

# Specific test file
docker-compose exec web pytest apps/products/tests/
```

### Database Operations

```powershell
# PostgreSQL CLI
docker-compose exec db psql -U ecommerce_user -d ecommerce_db

# Backup database
docker-compose exec db pg_dump -U ecommerce_user -d ecommerce_db > backup.sql

# Restore database
docker-compose exec -T db psql -U ecommerce_user -d ecommerce_db < backup.sql
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Docker daemon not running | Start Docker Desktop app |
| Port 8000 already in use | Change port in docker-compose.yml |
| Database won't connect | Check DB is healthy: `docker-compose ps db` |
| Celery tasks not running | Check RabbitMQ is healthy, restart Celery |
| Static files not loading | Run `docker-compose exec web python manage.py collectstatic --noinput` |
| Out of memory | Increase Docker Desktop memory limit |
| Containers keep restarting | Check logs: `docker-compose logs` |

---

## 📚 Next Steps

1. ✅ Docker Desktop installed
2. ✅ `.env` file created
3. ✅ `docker-compose build` completed
4. ✅ `docker-compose up -d` started
5. ✅ Services healthy (`docker-compose ps`)
6. ✅ Migrations run
7. ✅ Access API at http://localhost:8000/api/docs/
8. ✅ Test some endpoints
9. ✅ Review logs
10. ✅ Develop and deploy!

---

## 🎯 What You Have Now

✅ **Full Production-Like Environment:**
- PostgreSQL database (not SQLite)
- Redis caching
- RabbitMQ message broker
- Celery async workers
- Celery Beat scheduler
- Nginx reverse proxy
- Isolated containers
- Volume persistence

✅ **All 40+ API Endpoints Working:**
- Authentication & JWT
- Product catalog
- Shopping cart
- Orders
- Payments
- User management
- etc.

✅ **Auto-Generated Documentation:**
- Swagger UI at /api/docs/
- Full API reference
- Try-it-out capability

✅ **Monitoring & Logs:**
- Real-time logging
- Health checks
- Service status

---

**🚀 Docker setup complete! Your application is now running in production-like containers.** 🐳
