# Railway Deployment Checklist & Testing Guide

## 🔍 Pre-Deployment Testing (Local)

### 1. Test Docker Build
```bash
cd c:\Users\ALSAINT\Desktop\alx-project-nexus

# Remove old containers
docker-compose down --remove-orphans

# Build fresh images
docker-compose build --no-cache

# Check for build errors
echo "Build completed. Check above for any errors."
```

✅ **Success Indicator**: No ERROR messages in build output

### 2. Start Services
```bash
# Start all services
docker-compose up -d

# Wait for services to be ready
sleep 30

# Check status
docker-compose ps
```

✅ **Success Indicator**: All services show "Up" status

### 3. Run Migrations
```bash
# Apply database migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser --noinput --username admin --email admin@example.com
# Set password when prompted or use:
# echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin123')" | docker-compose exec web python manage.py shell
```

✅ **Success Indicator**: Migrations complete without errors

### 4. Test API Endpoints
```bash
# Test products endpoint
curl http://localhost/api/v1/products/

# Test auth endpoint  
curl -X POST http://localhost/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'

# Test admin panel
open http://localhost/admin/
```

✅ **Success Indicator**: API returns 200 OK responses

### 5. Check Logs
```bash
# View web service logs
docker-compose logs -f web

# Check for errors
docker-compose logs web | grep -i error

# View all services logs
docker-compose logs
```

✅ **Success Indicator**: No ERROR messages, services running normally

### 6. Verify Database
```bash
# Connect to database
docker-compose exec db psql -U postgres -d ecommerce -c "SELECT COUNT(*) FROM auth_user;"

# Check tables
docker-compose exec db psql -U postgres -d ecommerce -c "\dt"
```

✅ **Success Indicator**: Database has tables and data

## 🔧 Fix Issues If Found

### Issue: "ModuleNotFoundError: No module named 'config'"
**Fix**:
```bash
# Verify PYTHONPATH is set in Dockerfile
docker inspect ecommerce_web | grep PYTHONPATH

# If not set, rebuild with:
docker-compose build --no-cache web
docker-compose up -d web
```

### Issue: "ALLOWED_HOSTS doesn't match"
**Fix**:
```bash
# Check current ALLOWED_HOSTS in settings
docker-compose exec web python manage.py shell -c "from django.conf import settings; print(settings.ALLOWED_HOSTS)"

# Update in .env
# Add to ALLOWED_HOSTS=localhost,127.0.0.1,your.domain.com
docker-compose restart web
```

### Issue: "Database connection refused"
**Fix**:
```bash
# Check database status
docker-compose ps db

# Check database logs
docker-compose logs db

# Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

### Issue: "Static files 404"
**Fix**:
```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check static volume
docker inspect alx-project-nexus_static_volume

# Restart nginx
docker-compose restart nginx
```

## ✅ Pre-Deployment Verification

- [ ] Docker build completes without errors
- [ ] All services run successfully (`docker-compose ps`)
- [ ] Database migrations complete
- [ ] API returns 200 OK responses
- [ ] No error messages in logs
- [ ] Admin panel accessible
- [ ] Static files load correctly
- [ ] All environment variables set in `.env`

## 📤 Deploy to Railway

### Step 1: Prepare Git
```bash
# Ensure you're in project directory
cd c:\Users\ALSAINT\Desktop\alx-project-nexus

# Add all changes
git add .

# Commit
git commit -m "Production ready: Add Railway deployment files"

# Push to GitHub
git push origin main
```

✅ **Check**: Files are pushed to GitHub

### Step 2: Create Railway Project
1. Go to [railway.app](https://railway.app)
2. Log in or sign up
3. Click "New Project"
4. Select "Deploy from GitHub"
5. Authorize GitHub access
6. Select your repository
7. Select `main` branch
8. Railway will auto-detect and start building

✅ **Check**: Build started in Railway dashboard

### Step 3: Add Environment Variables

In Railway Dashboard → Project → Variables:

**Critical Variables**:
```
DJANGO_SETTINGS_MODULE=config.settings.production
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-50-chars-min
ALLOWED_HOSTS=yourdomain.railway.app,*.railway.app
POSTGRES_DB=ecommerce
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password-here
DB_HOST=postgres.railway.internal
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
```

**Email Variables** (for notifications):
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password
```

**Stripe Variables**:
```
STRIPE_PUBLIC_KEY=pk_test_your_key_or_pk_live_for_production
STRIPE_SECRET_KEY=sk_test_your_key_or_sk_live_for_production
```

✅ **Check**: All variables entered correctly

### Step 4: Add Database Service
1. In Railway Project → Click "Add Service"
2. Select "Database"
3. Choose "PostgreSQL"
4. Railway auto-generates connection variables
5. Verify `POSTGRES_*` variables appear

✅ **Check**: PostgreSQL service connected

### Step 5: Add Redis Service (Optional)
1. Click "Add Service"
2. Select "Redis"
3. Auto-generates `REDIS_URL`

✅ **Check**: Redis service ready (optional)

### Step 6: Configure Start Command
In Railway → Deployment → Settings → Start Command:
```bash
bash scripts/railway_startup.sh
```

Or simpler (Railway will auto-detect from Dockerfile):
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 4 --threads 2
```

✅ **Check**: Start command set correctly

## 🚀 Monitor Deployment

### View Build Logs
```bash
# In Railway Dashboard → Deployments → Latest
# Click to view real-time logs
```

### View Application Logs
```bash
railway login
railway link  # Link to your project
railway logs -f  # Follow logs
```

### Run Commands in Production
```bash
# Run migrations after first deploy
railway run python manage.py migrate

# Create superuser
railway run python manage.py createsuperuser

# Seed data
railway run python manage.py loaddata seed_data.json

# Check health
railway run python manage.py check
```

## ✅ Post-Deployment Testing

### 1. Test API Endpoints
```bash
# Get your Railway domain (from dashboard)
DOMAIN="yourdomain.railway.app"

# Test products
curl https://$DOMAIN/api/v1/products/

# Test auth
curl https://$DOMAIN/api/v1/auth/login/ -X POST

# Test admin
curl https://$DOMAIN/admin/
```

✅ **Success**: Endpoints return 200 OK (200, 401 for login without credentials is OK)

### 2. Test Admin Panel
```bash
# Open in browser
https://yourdomain.railway.app/admin/

# Login with superuser credentials
# Verify you can access database objects
```

✅ **Success**: Admin panel loads and is accessible

### 3. Test API Documentation
```bash
# Swagger documentation should be available
https://yourdomain.railway.app/api/docs/
```

✅ **Success**: API documentation displays

### 4. Check Database
```bash
# From Railway shell
railway run python manage.py dbshell

# Then in psql:
SELECT COUNT(*) FROM auth_user;
\dt  # List all tables
```

✅ **Success**: Database has tables and data

### 5. Monitor Logs for Errors
```bash
railway logs | grep -i error
```

✅ **Success**: No ERROR messages in logs

## 🎉 Success Indicators

- ✅ Build completes in Railway Dashboard
- ✅ Deploy shows "Live" status
- ✅ No errors in deployment logs
- ✅ API endpoints return responses
- ✅ Admin panel is accessible
- ✅ No error messages when accessing services
- ✅ Database migrations ran successfully
- ✅ Static files load properly

## 🔐 Final Security Checklist

Before marking as "Production Ready":

- [ ] `DEBUG=False` (not True)
- [ ] `SECRET_KEY` is long (50+ chars) and random
- [ ] `ALLOWED_HOSTS` includes only your domain(s)
- [ ] Email credentials are app-specific passwords, not main password
- [ ] Stripe keys are for correct environment (test/live)
- [ ] `.env` file is in `.gitignore` (never committed)
- [ ] HTTPS is enforced (`SECURE_SSL_REDIRECT=True`)
- [ ] Database password is strong
- [ ] No hardcoded secrets in code
- [ ] Admin credentials are changed from defaults

## 📞 Troubleshooting Commands

```bash
# SSH into Railway container
railway shell

# View environment variables
env | grep DJANGO

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Import Django config
python -c "import config; print(config.__file__)"

# Check database connection
python manage.py dbshell

# View running processes
ps aux

# Check disk space
df -h

# View error logs
tail -100 /app/logs/django.log

# Check migrations status
python manage.py showmigrations
```

## 📋 Issue Tracking

If something goes wrong, collect these for support:

```bash
# Get build logs
railway logs --tail 200 > build_logs.txt

# Get environment info
python manage.py check > check_result.txt

# Get migration status
python manage.py showmigrations > migrations.txt

# Share these files with support team
```

---

**Last Updated**: December 3, 2025  
**Status**: ✅ Ready for Deployment  
**Next Step**: Run local tests, then deploy to Railway!
