# Docker Setup Guide for E-Commerce Backend

## 📋 Prerequisites

### 1. Install Docker Desktop

**For Windows:**
- Download from: https://www.docker.com/products/docker-desktop
- Requirements:
  - Windows 10/11 Pro, Enterprise, or Education
  - At least 4GB RAM (8GB recommended)
  - Virtualization enabled in BIOS
  - WSL 2 (Windows Subsystem for Linux 2) installed

**Installation Steps:**
1. Download Docker Desktop for Windows
2. Run the installer
3. Follow the setup wizard
4. Accept the license agreement
5. Choose installation location
6. Wait for installation to complete
7. Restart your computer if prompted

### 2. Enable WSL 2 (If not already enabled)

```powershell
# Run as Administrator
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# Install WSL 2 Kernel
# Download from: https://aka.ms/wsl2kernel

# Set WSL 2 as default
wsl --set-default-version 2
```

### 3. Verify Installation

```powershell
docker --version
docker-compose --version
docker ps
```

---

## 🚀 Quick Start with Docker

### Step 1: Navigate to Project

```powershell
cd c:\Users\ALSAINT\Desktop\alx-project-nexus\e-commerce
```

### Step 2: Configure Environment Variables

Create `.env` file in the e-commerce directory:

```bash
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,web

# Database Settings
POSTGRES_DB=ecommerce_db
POSTGRES_USER=ecommerce_user
POSTGRES_PASSWORD=secure_password_123
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis Settings
REDIS_URL=redis://redis:6379/0

# Celery Settings
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/1

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587

# Stripe Settings
STRIPE_PUBLIC_KEY=pk_test_your_public_key
STRIPE_SECRET_KEY=sk_test_your_secret_key
```

### Step 3: Build Docker Images

```powershell
docker-compose build
```

This will:
- Pull base Python 3.11 image
- Install system dependencies
- Install Python packages from requirements.txt
- Create docker images for Django, Celery, and Celery Beat

### Step 4: Start Services

```powershell
docker-compose up -d
```

This starts (in detached mode):
- **PostgreSQL** database (port 5432)
- **Redis** cache (port 6379)
- **RabbitMQ** message broker (ports 5672, 15672)
- **Django** web application (port 8000)
- **Celery** worker
- **Celery Beat** scheduler
- **Nginx** reverse proxy (port 80, 443)

### Step 5: Verify Services

```powershell
# Check running containers
docker-compose ps

# Output should show:
# NAME                     STATUS
# ecommerce_db            Up (healthy)
# ecommerce_redis         Up (healthy)
# ecommerce_rabbitmq      Up (healthy)
# ecommerce_web           Up (healthy)
# ecommerce_celery        Up
# ecommerce_celery_beat   Up
# ecommerce_nginx         Up
```

### Step 6: Access the Application

**API Documentation:**
- http://localhost:8000/api/docs/ (via Nginx)
- or http://localhost:8000/api/docs/ (direct Django)

**Admin Panel:**
- http://localhost:8000/admin/

**RabbitMQ Management:**
- http://localhost:15672/
- Username: guest | Password: guest

**Logs:**
```powershell
docker-compose logs -f web      # Django logs
docker-compose logs -f celery   # Celery worker logs
docker-compose logs -f redis    # Redis logs
```

---

## 📦 Service Architecture

```
┌─────────────────────────────────────────────┐
│            Nginx (Port 80, 443)             │
│         Reverse Proxy & Load Balancer        │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
    Django Web            Static Files
    (Port 8000)           (CSS, JS, Images)
        │
        ├─► PostgreSQL DB (Port 5432)
        ├─► Redis Cache (Port 6379)
        └─► Celery Tasks
            │
            ├─► Celery Worker
            ├─► Celery Beat (Scheduler)
            └─► RabbitMQ Broker (Port 5672)
```

---

## 🔧 Docker Commands

### Container Management

```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View status
docker-compose ps

# View logs
docker-compose logs -f          # All services
docker-compose logs -f web      # Only Django
docker-compose logs -f celery   # Only Celery

# Stop specific service
docker-compose stop web
docker-compose start web

# Rebuild containers
docker-compose build --no-cache

# Remove all containers and volumes
docker-compose down -v
```

### Django Management Commands

```powershell
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Shell access
docker-compose exec web python manage.py shell

# Database commands
docker-compose exec web python manage.py dbshell
```

### Database Management

```powershell
# Access PostgreSQL
docker-compose exec db psql -U ecommerce_user -d ecommerce_db

# Common PostgreSQL commands:
# \dt                 - List tables
# \d table_name       - Describe table
# SELECT * FROM...    - Query data
# \q                  - Exit

# Backup database
docker-compose exec db pg_dump -U ecommerce_user -d ecommerce_db > backup.sql

# Restore database
docker-compose exec -T db psql -U ecommerce_user -d ecommerce_db < backup.sql
```

### Redis Management

```powershell
# Access Redis CLI
docker-compose exec redis redis-cli

# Common Redis commands:
# PING                - Test connection
# KEYS *              - List all keys
# GET key_name        - Get value
# SET key value       - Set value
# FLUSHALL            - Clear all data
# EXIT                - Exit CLI
```

### Celery Management

```powershell
# View active tasks
docker-compose exec celery celery -A config inspect active

# View registered tasks
docker-compose exec celery celery -A config inspect registered

# Purge all pending tasks
docker-compose exec celery celery -A config purge
```

---

## 🐛 Troubleshooting

### Problem: Services Won't Start
```powershell
# Check Docker daemon is running
docker ps

# Verify Docker Desktop is running
# If not, start Docker Desktop application

# Check port conflicts (if ports are in use)
netstat -ano | findstr :8000
netstat -ano | findstr :5432
```

### Problem: Port Already in Use
```powershell
# Change ports in docker-compose.yml
# For example, change 8000:8000 to 8001:8000

# Or kill process using the port
# Find PID using netstat, then:
taskkill /PID <pid_number> /F
```

### Problem: Database Connection Error
```powershell
# Check if postgres is healthy
docker-compose ps db

# View postgres logs
docker-compose logs db

# Restart database
docker-compose restart db

# Recreate database
docker-compose down db
docker-compose up -d db
```

### Problem: Celery Tasks Not Running
```powershell
# Check Celery worker status
docker-compose logs celery

# Check RabbitMQ status
docker-compose logs rabbitmq

# Restart Celery
docker-compose restart celery

# Check message broker connection
docker-compose exec celery celery -A config inspect ping
```

### Problem: Static Files Not Loading
```powershell
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check volume mount in docker-compose.yml
# Verify static_volume is mounted correctly

# Restart Nginx
docker-compose restart nginx
```

### Problem: Out of Disk Space
```powershell
# Clean up Docker resources
docker system prune -a

# Remove unused volumes
docker volume prune

# Remove all images
docker image prune -a

# Check disk usage
docker system df
```

---

## 📊 Monitoring Services

### Docker Stats

```powershell
# View real-time resource usage
docker stats

# View specific container stats
docker stats ecommerce_web ecommerce_db
```

### Health Checks

```powershell
# Check service health
docker-compose ps

# Manual health check
docker-compose exec web curl http://localhost:8000/health/
docker-compose exec redis redis-cli ping
docker-compose exec db pg_isready -U ecommerce_user
```

---

## 🔐 Security Best Practices

### 1. Environment Variables
- Never commit `.env` to git
- Use strong passwords for database and admin
- Generate secure SECRET_KEY

### 2. Database Backups
```powershell
# Regular backups
docker-compose exec db pg_dump -U ecommerce_user -d ecommerce_db > backup_$(date +%Y%m%d).sql
```

### 3. Update Images
```powershell
# Pull latest base images
docker pull postgres:15-alpine
docker pull redis:7-alpine
docker pull rabbitmq:3-management-alpine

# Rebuild with latest images
docker-compose build --no-cache
docker-compose up -d
```

### 4. Secrets Management
- Use Docker Secrets for production (requires Docker Swarm/Kubernetes)
- Use environment files for development
- Rotate API keys regularly

---

## 🚢 Production Deployment

### 1. Use Production Settings
```powershell
# Edit environment
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
```

### 2. SSL/TLS Configuration
```powershell
# Update nginx.conf with SSL certificates
# Place certificates in volume or mount
```

### 3. Database Persistence
```powershell
# Ensure postgres_data volume is backed up
# Use external managed databases for critical data
```

### 4. Log Management
```powershell
# Configure log aggregation
# Use ELK stack (Elasticsearch, Logstash, Kibana)
# or CloudWatch, Datadog, etc.
```

### 5. Monitoring & Alerting
```powershell
# Use Prometheus + Grafana
# or cloud-based monitoring services
```

---

## 📚 Example Workflows

### Complete Setup from Scratch

```powershell
# 1. Navigate to project
cd c:\Users\ALSAINT\Desktop\alx-project-nexus\e-commerce

# 2. Create environment file
echo "DEBUG=False
POSTGRES_DB=ecommerce_db
POSTGRES_USER=ecommerce_user
POSTGRES_PASSWORD=secure_password" > .env

# 3. Build images
docker-compose build

# 4. Start services
docker-compose up -d

# 5. Run migrations
docker-compose exec web python manage.py migrate

# 6. Create superuser
docker-compose exec web python manage.py createsuperuser

# 7. Seed data (if available)
docker-compose exec web python manage.py shell < scripts/seed_data.py

# 8. Access application
# http://localhost/api/docs/
```

### Development Workflow

```powershell
# Start services in foreground (see logs)
docker-compose up

# In another terminal:
# Make code changes
# Services auto-reload (if configured)

# Run specific commands
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Stop with Ctrl+C
```

### Testing

```powershell
# Run tests in container
docker-compose exec web pytest

# Run with coverage
docker-compose exec web pytest --cov=apps

# Run specific test file
docker-compose exec web pytest apps/products/tests/test_views.py
```

---

## 📖 Additional Resources

- **Docker Docs:** https://docs.docker.com/
- **Docker Compose:** https://docs.docker.com/compose/
- **PostgreSQL Docker:** https://hub.docker.com/_/postgres
- **Redis Docker:** https://hub.docker.com/_/redis
- **Django Docker:** https://docs.djangoproject.com/en/5.0/howto/deployment/containers/

---

## ✅ Checklist for Docker Setup

- [ ] Docker Desktop installed
- [ ] WSL 2 enabled
- [ ] `docker --version` shows version
- [ ] `docker-compose --version` shows version
- [ ] `.env` file created with credentials
- [ ] `docker-compose build` completes successfully
- [ ] `docker-compose up -d` starts all services
- [ ] `docker-compose ps` shows all healthy
- [ ] API accessible at http://localhost:8000/api/docs/
- [ ] Admin panel accessible at http://localhost:8000/admin/
- [ ] Database migrations completed
- [ ] Superuser created

---

**Your Docker setup is complete! You're ready to develop with Docker.** 🐳🚀
