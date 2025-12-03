# 🎯 Railway Deployment - Quick Reference Card

## ⚡ The 3-Minute Fix

### What was broken:
```
ModuleNotFoundError: No module named 'config'
```

### How I fixed it:
```dockerfile
# Added to Dockerfile
ENV PYTHONPATH=/app
```

### Why it works:
```
PYTHONPATH=/app tells Python to look in /app for modules
config module is in /app/config ← Python finds it ✅
```

---

## 📋 Before You Deploy

### Local Testing Checklist
```bash
cd c:\Users\ALSAINT\Desktop\alx-project-nexus

# 1. Clean build
docker-compose down --remove-orphans
docker-compose build --no-cache

# 2. Start services
docker-compose up -d
sleep 30

# 3. Test API
curl http://localhost/api/v1/products/

# 4. Check logs
docker-compose logs web | grep -i error

# ✅ If no errors → Ready for Railway
```

---

## 🚀 Deploy to Railway (5 steps)

### 1. Push to GitHub
```bash
git add .
git commit -m "Fix Railway deployment"
git push origin main
```

### 2. Create Railway Project
- Go to railway.app
- Click "New Project"
- "Deploy from GitHub"
- Select your repository

### 3. Set Environment Variables
Copy-paste these into Railway Dashboard → Variables:
```
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=<generate-50-char-random-key>
ALLOWED_HOSTS=yourdomain.railway.app
POSTGRES_DB=ecommerce
POSTGRES_USER=postgres
POSTGRES_PASSWORD=<strong-password>
DB_HOST=postgres.railway.internal
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
STRIPE_PUBLIC_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
```

### 4. Add PostgreSQL
- Click "Add Service"
- Select "Database"
- Choose "PostgreSQL"
- Railway auto-configures connection

### 5. Wait & Monitor
- Railway builds automatically
- Watch logs in dashboard
- When "Live" appears → Deployment complete

---

## ✅ After Deployment

### Test Everything
```bash
# Test API
curl https://yourdomain.railway.app/api/v1/products/

# Test Admin
open https://yourdomain.railway.app/admin/

# Run Migrations
railway run python manage.py migrate

# Check Health
railway run python manage.py check

# View Logs
railway logs -f
```

---

## 🆘 If Something Goes Wrong

### Error: "ModuleNotFoundError: config"
```bash
# Check if fix was applied
docker inspect ecommerce_web | grep PYTHONPATH
# Should show: PYTHONPATH=/app

# If not, rebuild:
docker-compose build --no-cache web
```

### Error: "ALLOWED_HOSTS doesn't match"
```bash
# Update Railway variable
ALLOWED_HOSTS=yourdomain.railway.app

# Restart service
railway restart
```

### Error: "Database connection refused"
```bash
# Check PostgreSQL service exists in Railway
# Check DATABASE_URL is set
# Wait 30+ seconds for database to boot

# Test locally first
docker-compose ps db
docker-compose logs db
```

### Error: "Static files 404"
```bash
# Collect static files
railway run python manage.py collectstatic --noinput

# Or let Dockerfile do it automatically (already configured)
```

---

## 📊 Files Created/Modified

| File | Status | Purpose |
|------|--------|---------|
| `/Dockerfile` | ✅ UPDATED | Added PYTHONPATH |
| `/e-commerce/config/settings/production.py` | ✅ NEW | Production config |
| `/railway.json` | ✅ NEW | Railway build config |
| `/scripts/railway_startup.sh` | ✅ NEW | Auto-migration script |
| `/.env.railway` | ✅ NEW | Env variables template |
| All documentation | ✅ NEW | Guides & checklists |

---

## 🔑 Key Environment Variables

| Variable | Example | Where |
|----------|---------|-------|
| DJANGO_SETTINGS_MODULE | config.settings.production | Railway |
| DEBUG | False | Railway |
| SECRET_KEY | <50-char-random> | Railway |
| ALLOWED_HOSTS | yourdomain.railway.app | Railway |
| DATABASE_URL | postgresql://... | Railway (auto) |
| REDIS_URL | redis://... | Railway (auto) |

---

## 💡 Pro Tips

1. **Generate SECRET_KEY**:
   ```python
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **View Logs in Real-Time**:
   ```bash
   railway logs -f
   ```

3. **SSH into Container**:
   ```bash
   railway shell
   python manage.py dbshell
   ```

4. **Test Before Committing**:
   ```bash
   docker-compose up -d && curl http://localhost/api/v1/products/
   ```

5. **Keep `.env` Out of Git**:
   ```bash
   # Already in .gitignore
   git status  # Verify .env is not listed
   ```

---

## 🎯 Deployment Flow

```
Local Code → Git Push → Railway Auto-Build → Test API → ✅ Live
    ↓            ↓              ↓             ↓
  Test      Commit &      Docker Build    Check
 Docker     Push to        Migrations    Endpoints
            GitHub         Static Files
```

---

## 📱 Quick Commands

```bash
# LOCAL
docker-compose build --no-cache
docker-compose up -d
docker-compose logs -f web
curl http://localhost/api/v1/products/

# RAILWAY
railway login
railway logs -f
railway run python manage.py migrate
railway shell

# GIT
git add .
git commit -m "Deploy to Railway"
git push origin main
```

---

## ✨ Success Indicators

- ✅ Build succeeds in Railway
- ✅ No ERROR messages in logs
- ✅ Deployment shows "Live"
- ✅ API returns 200 responses
- ✅ Admin panel works
- ✅ Database has data

---

## 🚨 Critical Don'ts

- ❌ Don't commit `.env` file
- ❌ Don't use DEBUG=True in production
- ❌ Don't hardcode secrets in code
- ❌ Don't forget ALLOWED_HOSTS
- ❌ Don't skip migrations

---

## 📞 When You Need Help

1. **Check Logs**: `railway logs -f` or dashboard
2. **Read Error**: What file/module is missing?
3. **Test Locally**: Does it work in Docker?
4. **Review Docs**: RAILWAY_QUICK_START.md
5. **Check Variables**: Are all env vars set?

---

## 🎓 What Changed?

### Before ❌
```dockerfile
WORKDIR /app
# PYTHONPATH not set
COPY . .
CMD ["gunicorn", "config.wsgi:application", ...]
# Python can't find config module
```

### After ✅
```dockerfile
ENV PYTHONPATH=/app
WORKDIR /app
COPY . .
CMD ["gunicorn", "config.wsgi:application", ...]
# Python finds config module in /app/config
```

---

## 📚 Documentation Map

- **Quick Start**: `RAILWAY_QUICK_START.md` ← Start here
- **Detailed Guide**: `RAILWAY_DEPLOYMENT.md` ← Full instructions
- **Troubleshooting**: `DEPLOYMENT_CHECKLIST.md` ← Issues & fixes
- **Visual Flow**: `DEPLOYMENT_GUIDE_VISUAL.md` ← Diagrams
- **Summary**: `DEPLOYMENT_SUMMARY.md` ← Overview

---

**Version**: 1.0  
**Last Updated**: December 3, 2025  
**Status**: ✅ Ready to Deploy

🚀 **Next Step**: Run `docker-compose build && docker-compose up -d`, then deploy to Railway!
