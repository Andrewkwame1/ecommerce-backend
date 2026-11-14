# Railway Deployment - Quick Start Guide

## ✅ Quick Fix for "ModuleNotFoundError: No module named 'config'"

Your Docker setup has a working directory issue. The `config` module is inside `e-commerce/` but Gunicorn can't find it.

### **Immediate Solution (for Railway)**

1. **Update your Dockerfile** - Already done ✅
   - Added `PYTHONPATH=/app` environment variable
   - Corrected WORKDIR to `/app`
   - Updated gunicorn command

2. **Update docker-compose.yml** - Already done ✅
   - Build context points to `./e-commerce`
   - Volumes point to correct directories

3. **Test Locally First**:
   ```bash
   cd alx-project-nexus
   docker-compose down
   docker-compose build
   docker-compose up -d
   docker-compose logs -f web
   ```

4. **Verify API is accessible**:
   ```bash
   curl http://localhost:8000/api/v1/products/
   ```

## 🚀 Deploy to Railway

### **Step 1: Prepare Your Project**

```bash
# Ensure all files are committed
git status
git add .
git commit -m "Prepare for Railway deployment"
```

### **Step 2: Connect Railway**

1. Go to [railway.app](https://railway.app)
2. Create a new project
3. Click "Deploy from GitHub" 
4. Select your repository
5. Railway auto-detects the Dockerfile and builds

### **Step 3: Configure Environment Variables**

In Railway Dashboard → Variables:

```
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=your-long-random-key-here
ALLOWED_HOSTS=yourdomain.railway.app
POSTGRES_DB=ecommerce
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure-password
DB_HOST=postgres.railway.internal
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
STRIPE_PUBLIC_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### **Step 4: Add PostgreSQL Service**

1. Click "Add Service" in Railway
2. Select "Database"
3. Choose "PostgreSQL"
4. Railway auto-links to your app
5. Environment variables are auto-populated

### **Step 5: Monitor Deployment**

View real-time logs:
```bash
railway login
railway shell
cat /app/logs/django.log
```

Or in Railway Dashboard → Deployments → Click latest → View Logs

## 🔍 Troubleshooting

### **Error: ModuleNotFoundError: No module named 'config'**

**Root Cause**: Django app can't import the config module because Python path is wrong

**Solution**:
```dockerfile
# In Dockerfile, add PYTHONPATH
ENV PYTHONPATH=/app
WORKDIR /app
```

**Verify Fix**:
```bash
docker exec ecommerce_web python -c "import config; print(config.__file__)"
```

### **Error: No module named 'django_extensions'**

**Root Cause**: Package not in requirements.txt

**Solution**:
```bash
pip install django-extensions django-debug-toolbar
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add missing packages"
git push
```

Railway will auto-rebuild.

### **Error: ALLOWED_HOSTS doesn't match request**

**Solution** in Railway Dashboard:
```
ALLOWED_HOSTS=yourdomain.railway.app,www.yourdomain.railway.app
```

Or dynamically in `config/settings/production.py`:
```python
if 'RAILWAY_DOMAIN' in os.environ:
    ALLOWED_HOSTS.append(os.getenv('RAILWAY_DOMAIN'))
```

### **Error: staticfiles not collected**

**Solution**: Dockerfile already handles this with:
```dockerfile
RUN python manage.py collectstatic --noinput 2>/dev/null || true
```

Or run manually:
```bash
railway run python manage.py collectstatic --noinput
```

### **Error: Database connection refused**

**Check**:
1. DATABASE_URL is set correctly
2. Database service is connected
3. Wait 30+ seconds for database to be ready

**Verify in container**:
```bash
railway run python manage.py migrate
```

### **Error: Worker failed to boot**

**Check Dockerfile**:
- PYTHONPATH is set
- WORKDIR is correct
- All requirements are installed
- No syntax errors in settings

**Fix**:
```bash
docker build -t test . 2>&1 | tail -50
```

## 📊 Monitoring

### **View Application Logs**
```bash
railway logs -f
```

### **SSH Into Container**
```bash
railway shell
```

### **Run Django Commands**
```bash
railway run python manage.py migrate
railway run python manage.py createsuperuser
railway run python manage.py loaddata seed_data.json
```

### **Check Environment Variables**
```bash
railway run env | grep DJANGO
```

## 🔐 Security Checklist

- [ ] `DEBUG=False` in production
- [ ] `SECRET_KEY` is long and random (50+ chars)
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] Database password is strong
- [ ] Don't commit `.env` to Git
- [ ] Use environment variables for all secrets

## 📝 Common Deployment Issues

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: config` | PYTHONPATH/WORKDIR wrong | Set `PYTHONPATH=/app` |
| `ALLOWED_HOSTS` error | Domain not in list | Add domain to `ALLOWED_HOSTS` var |
| Database connection refused | DB not ready/not connected | Wait 30s, check DATABASE_URL |
| staticfiles 404 | Not collected | Run collectstatic in Dockerfile |
| Worker failed to boot | Missing dependency | Check requirements.txt |
| CORS error from frontend | CORS_ALLOWED_ORIGINS wrong | Update var with frontend domain |
| Stripe webhook fails | Secret key wrong | Verify `STRIPE_SECRET_KEY` |

## ✅ Deployment Verification

After deployment, verify everything works:

```bash
# Check API is up
curl https://yourdomain.railway.app/api/v1/products/

# Check admin panel
open https://yourdomain.railway.app/admin/

# Check health endpoint (if exists)
curl https://yourdomain.railway.app/health/

# Check static files
curl https://yourdomain.railway.app/static/admin/css/base.css

# Check logs for errors
railway logs -f
```

## 🎉 Success Indicators

- ✅ Deployment shows "Live" in Railway Dashboard
- ✅ No errors in logs when accessing API
- ✅ Database migrations run successfully
- ✅ API returns 200 OK responses
- ✅ Admin panel is accessible
- ✅ Static files load properly

## 📞 Need Help?

1. Check Railway Docs: https://docs.railway.app
2. Check Django Docs: https://docs.djangoproject.com
3. View full logs: `railway logs --tail 100`
4. SSH into container: `railway shell`
5. Run diagnostic: `railway run python manage.py check`
