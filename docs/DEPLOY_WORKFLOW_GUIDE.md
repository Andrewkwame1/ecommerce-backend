# Deploy Workflow - Quick Reference

**Last Updated:** December 5, 2025

---

## What the Deploy Workflow Does

When you push to `main` or `master` branch, GitHub Actions automatically:

1. ✅ **Validates Docker Credentials** - Checks `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets exist
2. ✅ **Validates Python Syntax** - Compiles `config/settings/base.py` and `config/settings/production.py`
3. ✅ **Builds Docker Image** - Creates production-ready Docker image
4. ✅ **Pushes to Docker Hub** - Uploads image with multiple tags
5. ✅ **Updates Kubernetes** - Provides deployment manifest (optional)

---

## Required GitHub Secrets

### Step 1: Navigate to Repository Settings
```
https://github.com/Andrewkwame1/ecommerce-backend/settings/secrets/actions
```

### Step 2: Create These Secrets

**DOCKER_USERNAME**
- Value: Your Docker Hub username (e.g., `andrewkwame1`)
- Get from: https://hub.docker.com (top-right profile menu)

**DOCKER_PASSWORD**  
- Value: Docker Hub access token (NOT your password!)
- Get from: https://hub.docker.com/settings/security
- Steps:
  1. Go to `Account Settings` > `Security`
  2. Click `New Access Token`
  3. Name: `github-actions-deploy`
  4. Permissions: `Read & Write`
  5. Copy the token and paste into GitHub secret

---

## Docker Tags Generated

Each push generates multiple image tags:

```
ecommerce-api:latest                 # Always points to latest
ecommerce-api:main                   # Current branch name
ecommerce-api:20241205-abc12345      # Date + commit SHA
ecommerce-api:v1.0.0                 # For version tags (v1.0.0, etc.)
```

---

## Common Workflow Scenarios

### Scenario 1: Pushing to Main Branch
```bash
git commit -m "feat: add new feature"
git push origin main
```
**Result:** Docker image built and pushed with `latest` tag

### Scenario 2: Creating a Release
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```
**Result:** Docker image tagged with `v1.0.0`

### Scenario 3: Manual Trigger
Go to: `Actions` > `Deploy - Build and Push Docker Image` > `Run workflow`  
**Result:** Builds and pushes using current branch

---

## Troubleshooting Workflow Failures

### Error: "Docker credentials not configured"
**Solution:** Add `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets (see Required Secrets above)

### Error: "Settings syntax is invalid"
**Solution:** 
```bash
cd e-commerce
python -m py_compile config/settings/base.py
python -m py_compile config/settings/production.py
```
Fix any syntax errors before pushing.

### Error: "Permission denied" on Docker push
**Solution:**
1. Verify Docker Hub token (not password) is used
2. Check token permissions: `Read & Write`
3. Try generating new token on Docker Hub

### Workflow Succeeds but Image Not in Docker Hub
**Solution:**
1. Check GitHub Actions run logs for build errors
2. Verify Docker Hub account has push permissions
3. Check Docker Hub credentials haven't expired

---

## Viewing Workflow Logs

1. Go to: https://github.com/Andrewkwame1/ecommerce-backend/actions
2. Click on the latest workflow run
3. Click on `build-and-push` job
4. Expand each step to see detailed logs

### Important Log Sections

**Validate Docker Credentials Step**
```
✓ Docker credentials are configured
```

**Validate Django Settings Step** (NEW)
```
✓ Django settings syntax is valid
```

**Log in to Docker Hub Step**
```
Login Succeeded
```

**Build and Push Step**
```
Successfully built [image-id]
Successfully tagged [docker-hub-image]
Pushed [image] with digest: sha256:...
```

---

## Using the Docker Image

### Pull from Docker Hub
```bash
docker pull andrewkwame1/ecommerce-api:latest
```

### Run Locally
```bash
docker run -d \
  -p 8000:8000 \
  -e DJANGO_SECRET_KEY=your-secret \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  andrewkwame1/ecommerce-api:latest
```

### Deploy to Kubernetes
Update `k8s/deployment.yaml`:
```yaml
spec:
  containers:
  - name: ecommerce-api
    image: andrewkwame1/ecommerce-api:latest
    # or specific tag:
    image: andrewkwame1/ecommerce-api:v1.0.0
```

---

## Environment Variables at Build Time

These are set during Docker build:

```
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=build-time-secret-key
DEBUG=False
PYTHONUNBUFFERED=1
```

These should be set at runtime (deployment):

```
DATABASE_URL=postgresql://...
ALLOWED_HOSTS=api.example.com
CORS_ALLOWED_ORIGINS=https://frontend.example.com
EMAIL_HOST_PASSWORD=...
STRIPE_SECRET_KEY=...
```

---

## Security Notes

✅ **Secrets are never logged** - GitHub masks secret values in logs  
✅ **No credentials in images** - Dummy keys used at build time  
✅ **Settings validated before build** - Syntax errors caught early  
✅ **Docker tokens expire** - Regenerate if errors occur  

---

## Next Steps After Successful Build

1. **Monitor Docker Hub**
   - Go to https://hub.docker.com/r/andrewkwame1/ecommerce-api
   - Verify image appears with expected tags

2. **Test Image Locally**
   ```bash
   docker pull andrewkwame1/ecommerce-api:latest
   docker run ... # see "Using the Docker Image" above
   ```

3. **Deploy to Production**
   - Update Render/Heroku/K8s with new image
   - Set required environment variables
   - Run migrations if needed

4. **Verify Deployment**
   - Check `/healthz/` endpoint
   - Check `/api/docs/` for API documentation
   - Test key endpoints

---

## Disabling Auto-Deploy

If you want to push without triggering the workflow:

```bash
git push -o ci.skip origin main
```

This skips GitHub Actions for that push.

---

## Questions?

Check these files for more info:
- `.github/workflows/deploy.yml` - Workflow definition
- `e-commerce/Dockerfile` - Docker image configuration
- `docs/SECURITY_AND_CONFIGURATION.md` - Security settings
- `docs/CI_CD_FIXES.md` - Database configuration

