# 🎯 Railway Deployment - Visual Flowchart & Quick Guide

## Problem → Solution Flow

```
┌─────────────────────────────────────────────────────────────┐
│               ModuleNotFoundError: config                   │
│                    ERROR FLOWCHART                          │
└─────────────────────────────────────────────────────────────┘

                    Railway Deployment ↓
                           ↓
                  Docker Build Starts ↓
                           ↓
         FROM python:3.11-slim (no PYTHONPATH) ↓
                           ↓
                    WORKDIR /app ↓
                           ↓
            COPY . . (copies all files) ↓
                           ↓
            gunicorn config.wsgi:application ↓
                           ↓
        Python tries: import config (WHERE IS IT?) ↓
                           ↓
    PYTHONPATH not set - can't find /app/config ✗ ↓
                           ↓
            ERROR: ModuleNotFoundError ❌ ✗
```

## Solution Applied

```
┌─────────────────────────────────────────────────────────────┐
│                    FIX APPLIED                              │
│         Add PYTHONPATH=/app to Dockerfile                   │
└─────────────────────────────────────────────────────────────┘

                    Railway Deployment ↓
                           ↓
                  Docker Build Starts ↓
                           ↓
  FROM python:3.11-slim
  ENV PYTHONPATH=/app ✅ (NOW SET!) ↓
                           ↓
                    WORKDIR /app ↓
                           ↓
            COPY . . (copies all files) ↓
                           ↓
            gunicorn config.wsgi:application ↓
                           ↓
        Python tries: import config ✓ ↓
                           ↓
     PYTHONPATH=/app tells Python to look in /app ↓
                           ↓
         Found /app/config module! ✓ ↓
                           ↓
              Django Initializes ✓ ↓
                           ↓
           Gunicorn Starts Server ✓ ↓
                           ↓
           🎉 SUCCESS: App Running! ✅
```

---

## Deployment Steps Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                   DEPLOYMENT FLOW                             │
└──────────────────────────────────────────────────────────────┘

STEP 1: Local Testing
┌─────────────────────────────────────────┐
│ git add . && git commit && git push     │
│ docker-compose build --no-cache         │
│ docker-compose up -d                    │
│ curl http://localhost/api/v1/products/  │
│ ✅ No errors? → Proceed to Step 2       │
└─────────────────────────────────────────┘

STEP 2: Create Railway Project
┌─────────────────────────────────────────┐
│ 1. Go to railway.app                    │
│ 2. New Project                          │
│ 3. Deploy from GitHub                   │
│ 4. Select repository & main branch      │
│ ✅ Build starts? → Proceed to Step 3    │
└─────────────────────────────────────────┘

STEP 3: Set Environment Variables
┌─────────────────────────────────────────┐
│ DJANGO_SETTINGS_MODULE=                 │
│   config.settings.production            │
│ DEBUG=False                             │
│ SECRET_KEY=your-50-char-random-key      │
│ ALLOWED_HOSTS=yourdomain.railway.app    │
│ DATABASE_URL=postgresql://...           │
│ REDIS_URL=redis://...                   │
│ ✅ Variables set? → Proceed to Step 4   │
└─────────────────────────────────────────┘

STEP 4: Add PostgreSQL Service
┌─────────────────────────────────────────┐
│ 1. Click "Add Service"                  │
│ 2. Select "Database"                    │
│ 3. Choose "PostgreSQL"                  │
│ 4. Railway auto-generates connection    │
│ ✅ PostgreSQL added? → Proceed to Step 5│
└─────────────────────────────────────────┘

STEP 5: Monitor Deployment
┌─────────────────────────────────────────┐
│ 1. View Deployment Logs                 │
│ 2. Wait for "Live" status               │
│ 3. Check for ERROR messages             │
│ 4. If errors: Review logs & fix         │
│ ✅ Live & no errors? → Proceed Step 6   │
└─────────────────────────────────────────┘

STEP 6: Post-Deployment Testing
┌─────────────────────────────────────────┐
│ 1. curl https://yourdomain/api/v1/...   │
│ 2. Test admin panel                     │
│ 3. Run migrations: railway run python   │
│    manage.py migrate                    │
│ 4. Create superuser if needed           │
│ ✅ All working? → DEPLOYMENT COMPLETE   │
└─────────────────────────────────────────┘
```

---

## File Organization

```
alx-project-nexus/
│
├── 📁 e-commerce/                      (Django project root)
│   ├── 📁 config/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   ├── production.py ← 🆕 PRODUCTION SETTINGS
│   │   │   └── test.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   │
│   ├── 📁 apps/                        (6 Django apps)
│   │   ├── users/
│   │   ├── products/
│   │   ├── cart/
│   │   ├── orders/
│   │   ├── payments/
│   │   └── notifications/
│   │
│   ├── 📁 scripts/
│   │   └── railway_startup.sh ← 🆕 STARTUP SCRIPT
│   │
│   ├── Dockerfile                      ← ✅ UPDATED
│   ├── manage.py
│   └── requirements.txt
│
├── 📄 Dockerfile                       ← 🆕 ROOT DOCKERFILE
├── 📄 docker-compose.yml               (unchanged)
├── 📄 railway.json                     ← 🆕 RAILWAY CONFIG
├── 📄 .env.example                     ← ✅ UPDATED
├── 📄 .env.railway                     ← 🆕 ENV TEMPLATE
│
├── 📚 DOCUMENTATION (All 🆕 NEW):
│   ├── DEPLOYMENT_SUMMARY.md
│   ├── RAILWAY_FIX_SUMMARY.md
│   ├── RAILWAY_QUICK_START.md
│   ├── RAILWAY_DEPLOYMENT.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   └── ERD.md
│
└── 📄 README.md
```

---

## Environment Variables - Quick Ref

```
┌──────────────────────────────────────────────────────────┐
│      REQUIRED VARIABLES FOR RAILWAY DEPLOYMENT           │
└──────────────────────────────────────────────────────────┘

DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=[Generate using: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"]
ALLOWED_HOSTS=yourdomain.railway.app

Database (PostgreSQL):
  POSTGRES_DB=ecommerce
  POSTGRES_USER=postgres
  POSTGRES_PASSWORD=[strong-random-password]
  DB_HOST=postgres.railway.internal
  DB_PORT=5432

Caching & Async (Redis):
  REDIS_URL=redis://redis:6379/0
  CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//

Email (Gmail):
  EMAIL_HOST=smtp.gmail.com
  EMAIL_PORT=587
  EMAIL_HOST_USER=[your-email@gmail.com]
  EMAIL_HOST_PASSWORD=[app-specific-password, not main password]

Payment (Stripe):
  STRIPE_PUBLIC_KEY=[pk_live_... or pk_test_...]
  STRIPE_SECRET_KEY=[sk_live_... or sk_test_...]
```

---

## Troubleshooting Decision Tree

```
┌──────────────────────────────────────────────────────────┐
│           ERROR DIAGNOSIS FLOWCHART                      │
└──────────────────────────────────────────────────────────┘

    ERROR: ModuleNotFoundError
              │
              ├─→ Check: PYTHONPATH in Dockerfile? ✅
              │
              ├─→ Check: WORKDIR /app is set? ✅
              │
              ├─→ Check: Dockerfile build context? ✅
              │
              └─→ Run: docker-compose build --no-cache
                       docker-compose up -d
                       curl http://localhost/api/v1/products/

    ERROR: ALLOWED_HOSTS mismatch
              │
              ├─→ Check: Domain in ALLOWED_HOSTS variable? 
              │   └─→ Add it: ALLOWED_HOSTS=yourdomain.railway.app
              │
              ├─→ Restart: docker-compose restart web
              │
              └─→ Test: curl https://yourdomain.railway.app/

    ERROR: Database connection refused
              │
              ├─→ Check: PostgreSQL service running?
              │
              ├─→ Check: DATABASE_URL variable set?
              │
              ├─→ Check: Credentials correct?
              │
              └─→ Reset: docker-compose down -v
                       docker-compose up -d
                       docker-compose exec web python manage.py migrate

    ERROR: Static files 404
              │
              ├─→ Run: docker-compose exec web python manage.py collectstatic
              │
              ├─→ Check: STATIC_ROOT is writable
              │
              └─→ Restart: docker-compose restart nginx

    ERROR: Worker failed to boot
              │
              ├─→ Check: Build logs for import errors
              │
              ├─→ Check: requirements.txt has all packages
              │
              ├─→ Check: No syntax errors in settings
              │
              └─→ Test: docker build -t test . 2>&1 | tail -100
```

---

## Quick Commands Reference

```bash
# LOCAL TESTING
docker-compose build --no-cache              # Rebuild without cache
docker-compose up -d                         # Start all services
docker-compose logs -f web                   # Watch web service logs
docker-compose exec web python manage.py ... # Run Django command
curl http://localhost/api/v1/products/       # Test API

# RAILWAY
railway login                                 # Authenticate with Railway
railway link                                  # Link to your project
railway logs -f                               # Watch production logs
railway run python manage.py migrate          # Run migrations
railway shell                                 # SSH into container
railway env                                   # View environment variables

# GIT
git add .                                     # Stage all changes
git commit -m "message"                       # Commit with message
git push origin main                          # Push to GitHub
git status                                    # Check what's changed
```

---

## Success Checklist ✅

After following the guide, you should have:

- ✅ Fixed Dockerfile with PYTHONPATH=/app
- ✅ Production settings configured
- ✅ Railway configuration files created
- ✅ Environment variables template created
- ✅ Startup script for migrations
- ✅ Comprehensive documentation
- ✅ Project tested locally
- ✅ Project deployed to Railway
- ✅ API endpoints tested and working
- ✅ Admin panel accessible
- ✅ Database migrations completed

---

## 🎓 Key Learning Points

1. **PYTHONPATH**: Tells Python where to find modules
   ```dockerfile
   ENV PYTHONPATH=/app
   ```

2. **WORKDIR**: Sets the working directory in container
   ```dockerfile
   WORKDIR /app
   ```

3. **Build Context**: Determines what's available during build
   ```yaml
   build:
     context: ./e-commerce  # This is the starting point
   ```

4. **Environment Variables**: Configure application without code changes
   ```
   DJANGO_SETTINGS_MODULE=config.settings.production
   ```

5. **Startup Script**: Runs migrations and starts server
   ```bash
   python manage.py migrate
   gunicorn config.wsgi:application
   ```

---

## 📞 Getting Help

If you're stuck:

1. **Check Logs First**:
   ```bash
   docker-compose logs -f web
   # or
   railway logs -f
   ```

2. **Read Error Message Carefully**:
   - Look for the exact line number
   - Understand what module/file is missing
   - Check if it's a configuration issue

3. **Test Locally First**:
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   curl http://localhost/api/v1/products/
   ```

4. **Ask Questions**:
   - Rails docs: https://docs.railway.app
   - Django docs: https://docs.djangoproject.com
   - Stack Overflow: Tag with `django` + `railway`

---

**Version**: 1.0  
**Last Updated**: December 3, 2025  
**Status**: ✅ COMPLETE & TESTED  

🚀 **You're ready to deploy!**
