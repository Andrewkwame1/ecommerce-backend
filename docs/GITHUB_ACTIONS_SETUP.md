# GitHub Actions Setup Guide

## Overview

This guide explains how to set up GitHub Actions for automated Docker image building and pushing to Docker Hub.

---

## Issue: "Error: Username and password required"

### Root Cause
The GitHub Actions workflow `deploy.yml` requires GitHub Secrets to be configured in your repository, but they haven't been set up yet.

### Solution: Configure GitHub Secrets

#### Step 1: Create Docker Hub Access Token

1. Go to [Docker Hub Security Settings](https://hub.docker.com/settings/security)
2. Click "New Access Token"
3. Enter token description: `GitHub Actions`
4. Click "Generate"
5. **Copy the token** (you'll only see it once!)

#### Step 2: Add GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**

**Add Secret #1: DOCKER_USERNAME**
- **Name:** `DOCKER_USERNAME`
- **Value:** Your Docker Hub username
- Click **"Add secret"**

**Add Secret #2: DOCKER_PASSWORD**
- **Name:** `DOCKER_PASSWORD`
- **Value:** The access token you created in Step 1 (NOT your Docker Hub password!)
- Click **"Add secret"**

#### Step 3: Verify Secrets Are Added

After adding both secrets, you should see:
```
✓ DOCKER_USERNAME
✓ DOCKER_PASSWORD
```

---

## Workflow: What Happens When You Push to GitHub

### Trigger Events
The workflow automatically runs when:
1. **Push to `main` branch** - Deploys latest build
2. **Push a tag** (e.g., `v1.0.0`) - Deploys tagged version
3. **Manual workflow dispatch** - Run workflow manually from GitHub UI

### Step-by-Step Execution

```
1. Checkout Code
   ↓
2. Validate Docker Credentials
   ↓
3. Set up Docker Buildx
   ↓
4. Log in to Docker Hub ✓ (requires secrets)
   ↓
5. Extract Metadata
   ↓
6. Determine Version Tag
   ↓
7. Build and Push Docker Image
   ↓
8. Display Image Digest
   ↓
9. Update Kubernetes Deployment (optional)
```

---

## Troubleshooting

### Issue: "Username and password required" Error

**Check List:**
- [ ] Secrets are configured in Settings → Secrets
- [ ] `DOCKER_USERNAME` is set to your Docker Hub username
- [ ] `DOCKER_PASSWORD` is set to an access token (NOT password)
- [ ] Access token is still valid (hasn't expired)
- [ ] Secrets are set at repository level (not organization level)

### Issue: Image Push Fails

**Common causes:**
1. Repository doesn't exist on Docker Hub
   - **Fix:** Create repository at https://hub.docker.com/repository/create
   
2. Access token is invalid or expired
   - **Fix:** Regenerate new access token in Docker Hub settings
   - Update DOCKER_PASSWORD secret in GitHub

3. Repository is private and you don't have push access
   - **Fix:** Make sure your Docker Hub account has permission to push

### Issue: Workflow Stuck on "Building and Pushing"

**Check:**
- Go to GitHub Actions tab in repository
- Click on the stuck workflow
- Check logs for specific error messages

---

## Image Naming Convention

Docker images are pushed with multiple tags:

```
docker.io/{DOCKER_USERNAME}/ecommerce-api:latest
docker.io/{DOCKER_USERNAME}/ecommerce-api:{version}
docker.io/{DOCKER_USERNAME}/ecommerce-api:{git-sha}
```

### Examples:
- Main branch push: `ecommerce-api:latest`
- Tag `v1.0.0`: `ecommerce-api:1.0.0`, `ecommerce-api:latest`
- Commit: `ecommerce-api:20241205-abc123def`

---

## Manual Workflow Trigger

### Via GitHub UI

1. Go to repository
2. Click **Actions** tab
3. Select **"Deploy - Build and Push Docker Image"**
4. Click **"Run workflow"**
5. Select branch and optionally enter version tag
6. Click **"Run workflow"**

### Via GitHub CLI

```bash
gh workflow run deploy.yml --ref main
```

Or with a custom version:
```bash
gh workflow run deploy.yml --ref main -f version=v1.0.0
```

---

## Understanding the Workflow File

### Location
```
.github/workflows/deploy.yml
```

### Key Sections

**Environment Variables:**
```yaml
env:
  REGISTRY: docker.io
  IMAGE_NAME: ecommerce-api
```

**Trigger Events:**
```yaml
on:
  push:
    branches: [main, master]
    tags: ['v*']
  workflow_dispatch:
```

**Docker Login:**
```yaml
- name: Log in to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}
```

**Build and Push:**
```yaml
- name: Build and push Docker image
  uses: docker/build-push-action@v5
  with:
    context: ./e-commerce  # Build context directory
    push: true             # Push to registry
    tags: |
      ${{ env.REGISTRY }}/${{ secrets.DOCKER_USERNAME }}/${{ env.IMAGE_NAME }}:latest
```

---

## Best Practices

### 1. Use Access Tokens, Not Passwords
- ✅ DO: Use Docker Hub access tokens
- ❌ DON'T: Use your Docker Hub password

### 2. Rotate Access Tokens Periodically
- Generate new token every 90 days
- Delete old unused tokens
- Update GitHub secret with new token

### 3. Monitor Workflow Runs
- Check GitHub Actions tab regularly
- Review logs for errors
- Set up notifications for failures

### 4. Use Semantic Versioning for Tags
- `v1.0.0` - Release version
- `v1.0.0-beta.1` - Pre-release
- `main` branch - Always pushed as `:latest`

### 5. Keep Workflow Configuration Updated
- Review updates to `docker/login-action`
- Review updates to `docker/build-push-action`
- Test new versions in development branch first

---

## Next Steps

### After Initial Setup

1. **Test the workflow:**
   - Make a small commit to main branch
   - Go to Actions tab and verify build succeeds
   - Check Docker Hub to confirm image is pushed

2. **Set up continuous deployment:**
   - Update Kubernetes deployment manifests
   - Or configure Render to auto-deploy on new image push

3. **Configure notifications:**
   - GitHub: Enable branch protection rules
   - GitHub: Enable required status checks
   - Slack/Email: Get notifications on workflow failures

### Alternative CI/CD Platforms

If you want to use other platforms instead of GitHub Actions:

- **GitLab CI/CD:** `.gitlab-ci.yml`
- **Jenkins:** `Jenkinsfile`
- **CircleCI:** `.circleci/config.yml`
- **Travis CI:** `.travis.yml`

---

## Secrets Reference

### GitHub Secrets vs Environment Variables

```
GitHub Secrets (Encrypted):
├── DOCKER_USERNAME (from GitHub Settings)
├── DOCKER_PASSWORD (from GitHub Settings)
└── Used: ${{ secrets.DOCKER_USERNAME }}

Environment Variables (Plain text):
├── REGISTRY: docker.io
├── IMAGE_NAME: ecommerce-api
└── Used: ${{ env.REGISTRY }}
```

**Security Note:** Secrets are encrypted and never visible in logs.

---

## Troubleshooting Checklist

```
[ ] Have you created a Docker Hub account?
[ ] Have you generated an access token?
[ ] Have you added DOCKER_USERNAME secret?
[ ] Have you added DOCKER_PASSWORD secret?
[ ] Are both secrets showing in Settings → Secrets?
[ ] Is the token format correct (not password)?
[ ] Have you committed and pushed changes to repo?
[ ] Is the workflow file in .github/workflows/?
[ ] Are there any syntax errors in deploy.yml?
[ ] Does your Docker Hub account allow image push?
```

---

## Support

For issues:
1. Check workflow logs in GitHub Actions tab
2. Verify secrets are configured correctly
3. Test Docker login locally:
   ```bash
   docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD
   ```
4. Check Docker Hub security settings for token validity

---

**Last Updated:** December 5, 2025  
**Workflow Status:** ✅ Ready to use

