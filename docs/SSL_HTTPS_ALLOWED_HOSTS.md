# SSL/HTTPS and ALLOWED_HOSTS Configuration Guide

## Overview

This document explains Django's SSL/HTTPS security settings and how they work with reverse proxies like Render, Heroku, AWS ALB, and Nginx.

---

## Quick Summary

| Setting | Value | Reason |
|---------|-------|--------|
| `SECURE_SSL_REDIRECT` | **False** ❌ | Reverse proxy already handles HTTPS |
| `SECURE_PROXY_SSL_HEADER` | **('HTTP_X_FORWARDED_PROTO', 'https')** ✅ | Trust reverse proxy's HTTPS info |
| `SESSION_COOKIE_SECURE` | **True** ✅ | Encrypt cookies in transit |
| `CSRF_COOKIE_SECURE` | **True** ✅ | Protect CSRF tokens |
| `ALLOWED_HOSTS` | **['*']** or **[RENDER_EXTERNAL_HOSTNAME]** | Accept requests from reverse proxy |

---

## Understanding the Problem

### Scenario: Traffic Flow to Your Django App

```
User's Browser (HTTPS)
         ↓
    [Internet]
         ↓
Render's Reverse Proxy (HTTPS → HTTP conversion)
         ↓
Django Application (HTTP - inside container)
```

### The Issue with SECURE_SSL_REDIRECT = True

If we enabled `SECURE_SSL_REDIRECT = True`:

```
1. User makes HTTPS request to reverse proxy
2. Reverse proxy converts to HTTP, forwards to Django
3. Django sees: protocol = HTTP
4. Django thinks: "Not HTTPS! Redirect to HTTPS!"
5. Django sends: Redirect to HTTPS://...
6. Browser receives redirect, makes HTTPS request
7. Loop repeats → Redirect loop ❌
```

### The Solution with SECURE_PROXY_SSL_HEADER

```
1. User makes HTTPS request to reverse proxy
2. Reverse proxy converts to HTTP, adds header: X-Forwarded-Proto: https
3. Django receives: HTTP protocol + X-Forwarded-Proto: https header
4. Django reads: "Original request was HTTPS (from header)"
5. Django trusts the header (SECURE_PROXY_SSL_HEADER setting)
6. Django proceeds normally with secure context ✅
```

---

## Configuration Details

### 1. SECURE_SSL_REDIRECT = False

**When to use:**
- ✅ Render, Heroku, AWS ALB (reverse proxy deployments)
- ✅ Docker containers behind Nginx
- ✅ Any deployment where reverse proxy handles HTTPS

**When NOT to use:**
- ❌ Direct internet access to Django (no reverse proxy)
- ❌ Standalone server with no load balancer

**Why False?**
```
If True → Automatic redirect from HTTP to HTTPS
Problem: Reverse proxy sends HTTP (but original is HTTPS)
Result: Redirect loop
```

### 2. SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

**What it does:**
- Tells Django to look at the `X-Forwarded-Proto` header
- If value is `'https'`, Django considers request as HTTPS
- Allows Django to generate HTTPS URLs in templates/responses

**How it works:**
```python
# Django checks this header
request.headers.get('X-Forwarded-Proto') == 'https'

# If true, it sets
request.is_secure() → True
```

**Why Render/Heroku set this:**
- They ensure all traffic is HTTPS before reaching your app
- The header proves the original request was HTTPS
- It's safe to trust on these platforms

### 3. SESSION_COOKIE_SECURE = True

**What it does:**
- Cookies only sent over HTTPS
- Prevents interception of session tokens

**Example:**
```
Browser Cookie Flag: Secure
└─ Only transmit over HTTPS
   └─ Blocks cookie if forced to HTTP
```

### 4. CSRF_COOKIE_SECURE = True

**What it does:**
- CSRF protection token only sent over HTTPS
- Prevents cross-site request forgery attacks

### 5. CSRF_TRUSTED_ORIGINS

**What it does:**
- Whitelist domains that can make cross-origin requests
- Prevents CSRF attacks from other domains

**Example:**
```python
CSRF_TRUSTED_ORIGINS = [
    'https://ecommerce-backend-1-v60x.onrender.com',
    'https://*.onrender.com',  # Wildcard for any subdomain
    'https://example.com',
]
```

---

## ALLOWED_HOSTS Debugging

### What is ALLOWED_HOSTS?

Security setting that prevents **Host Header Injection** attacks:

```
Attacker Request:
GET / HTTP/1.1
Host: attacker.com    ← Fake host

Django ALLOWED_HOSTS check:
If 'attacker.com' not in ALLOWED_HOSTS:
    Return 400 Bad Request ✓
```

### ALLOWED_HOSTS in Production

**Our Configuration:**
```python
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME', '')

if RENDER_EXTERNAL_HOSTNAME:
    # Render sets this automatically
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME, 'localhost', '127.0.0.1']
elif ALLOWED_HOSTS_ENV:
    # Manual configuration via environment variable
    ALLOWED_HOSTS = [host.strip() for host in ALLOWED_HOSTS_ENV.split(',')]
else:
    # Fallback: Accept any host (safe with reverse proxy validation)
    ALLOWED_HOSTS = ['*']
```

### Debugging Output

The production settings now log:
```
[PRODUCTION CONFIG] DEBUG=False, ALLOWED_HOSTS=['example.onrender.com'], ALLOWED_HOSTS_ENV='', RENDER_EXTERNAL_HOSTNAME='example.onrender.com'
```

This helps identify:
- Is Render setting RENDER_EXTERNAL_HOSTNAME?
- What hosts are being accepted?
- Is ALLOWED_HOSTS_ENV being used?

### How Render Sets This

When you deploy on Render:
1. Render auto-generates domain: `app-name-xxxxx.onrender.com`
2. Sets environment variable: `RENDER_EXTERNAL_HOSTNAME=app-name-xxxxx.onrender.com`
3. Django reads it and adds to ALLOWED_HOSTS
4. Your app automatically accepts that domain ✅

---

## Common Scenarios

### Scenario 1: Render Deployment

**Your URL:** `https://ecommerce-backend-1-v60x.onrender.com`

**What happens:**
```
1. User visits HTTPS URL (reverse proxy)
2. Render's reverse proxy handles HTTPS
3. Converts to HTTP, forwards to Django
4. Django receives:
   - Protocol: HTTP
   - Header: X-Forwarded-Proto: https
   - Host: ecommerce-backend-1-v60x.onrender.com
5. Django checks:
   - Is ecommerce-backend-1-v60x.onrender.com in ALLOWED_HOSTS? ✓
   - Is X-Forwarded-Proto: https? ✓
6. Request allowed, response generated
7. Render's reverse proxy sends HTTPS to user
```

**Settings required:**
```python
SECURE_SSL_REDIRECT = False  # Don't redirect (causes loop)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Trust header
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME]  # Set by Render
```

### Scenario 2: Custom Domain on Render

**Your domain:** `api.example.com` (CNAME to Render)

**Settings required:**
```python
# Environment variable (set in Render dashboard)
ALLOWED_HOSTS_ENV = "api.example.com,example.com"

# Django parses it
ALLOWED_HOSTS = ['api.example.com', 'example.com']
```

### Scenario 3: Multiple Subdomains

**Your domains:**
- `api.example.com`
- `api-staging.example.com`
- `api-test.example.com`

**Settings:**
```python
CSRF_TRUSTED_ORIGINS = [
    'https://api.example.com',
    'https://api-staging.example.com',
    'https://api-test.example.com',
    'https://*.example.com',  # Wildcard
]
```

---

## Testing HTTPS Configuration

### Check If HTTPS is Working

```bash
# Test with curl
curl -v https://ecommerce-backend-1-v60x.onrender.com/api/v1/products/

# Expected headers:
# SSL connection established ✓
# X-Forwarded-Proto: https (in server response)
```

### Check Cookies Are Secure

```bash
# Browser DevTools → Application → Cookies
Cookie Name: sessionid
├─ Value: xxxxx
├─ Domain: ecommerce-backend-1-v60x.onrender.com
├─ Path: /
├─ Expires: ...
├─ Secure: ✓ (encrypted in transit)
├─ HttpOnly: ✓ (not accessible from JavaScript)
└─ SameSite: Lax ✓ (CSRF protection)
```

### Check ALLOWED_HOSTS

```bash
# Try with wrong Host header
curl -H "Host: attacker.com" https://ecommerce-backend-1-v60x.onrender.com/api/v1/products/

# Expected response: 400 Bad Request
# Because attacker.com not in ALLOWED_HOSTS
```

### Enable Debug Logging

```bash
# In production, set environment variable
export DJANGO_LOG_LEVEL=DEBUG

# Or in Django shell
from django.conf import settings
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"SECURE_SSL_REDIRECT: {settings.SECURE_SSL_REDIRECT}")
print(f"SECURE_PROXY_SSL_HEADER: {settings.SECURE_PROXY_SSL_HEADER}")
```

---

## Troubleshooting

### Problem: "400 Bad Request" When Accessing Your Site

**Cause:** Host not in ALLOWED_HOSTS

**Solution:**
1. Check what host was in the request:
   ```python
   # In Django logs, look for:
   # Invalid HTTP_HOST header: 'wrong.domain.com'
   ```

2. Add host to ALLOWED_HOSTS:
   ```python
   ALLOWED_HOSTS = ['correct.domain.com', 'wrong.domain.com']
   ```

3. Or use environment variable:
   ```bash
   export ALLOWED_HOSTS="correct.domain.com,wrong.domain.com"
   ```

### Problem: Infinite Redirect Loop

**Cause:** SECURE_SSL_REDIRECT = True with reverse proxy

**Solution:**
```python
# Change to
SECURE_SSL_REDIRECT = False  # Not needed, proxy handles it

# Keep this to trust proxy's HTTPS info
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Problem: Cookies Not Being Sent

**Cause:** SESSION_COOKIE_SECURE = True but accessing via HTTP

**Solution:**
```python
# Make sure you're using HTTPS, not HTTP
# Or temporarily disable for testing (not for production)
SESSION_COOKIE_SECURE = False  # Only for testing!
```

### Problem: CSRF Token Validation Fails

**Cause:** Origin not in CSRF_TRUSTED_ORIGINS

**Solution:**
```python
# Add your domain to whitelist
CSRF_TRUSTED_ORIGINS = [
    'https://yourdomain.com',
    'https://*.yourdomain.com',
]
```

---

## Security Best Practices

### 1. Enable HSTS (HTTP Strict Transport Security)

After confirming HTTPS works:
```python
# Tell browsers to ALWAYS use HTTPS
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

**Warning:** Once enabled, browsers cache this for 1 year. Don't enable if HTTPS might be removed.

### 2. Use Whitelist, Not Wildcard

**Better:**
```python
ALLOWED_HOSTS = ['api.example.com', 'example.com']
```

**Acceptable:**
```python
ALLOWED_HOSTS = ['*.onrender.com']  # During development on Render
```

**Not recommended:**
```python
ALLOWED_HOSTS = ['*']  # Only if absolutely necessary
```

### 3. Monitor ALLOWED_HOSTS Errors

```python
# Log 400 errors for debugging
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}
```

### 4. Test Regularly

```bash
# Before deploying new domain
curl -H "Host: newdomain.com" https://yourdomain.com/
# Should get 400 if newdomain not in ALLOWED_HOSTS

# After adding to ALLOWED_HOSTS
curl -H "Host: newdomain.com" https://yourdomain.com/
# Should work normally
```

---

## Reference: Django Security Settings

| Setting | Purpose | Value |
|---------|---------|-------|
| `DEBUG` | Show error pages | `False` in production |
| `SECRET_KEY` | CSRF/session tokens | Unique, long string |
| `ALLOWED_HOSTS` | Host header validation | List of allowed domains |
| `SECURE_SSL_REDIRECT` | Force HTTPS | `False` with reverse proxy |
| `SECURE_PROXY_SSL_HEADER` | Trust proxy HTTPS info | `('HTTP_X_FORWARDED_PROTO', 'https')` |
| `SESSION_COOKIE_SECURE` | Encrypt cookies | `True` |
| `CSRF_COOKIE_SECURE` | Protect CSRF token | `True` |
| `SECURE_BROWSER_XSS_FILTER` | XSS protection | `True` |
| `SECURE_CONTENT_TYPE_NOSNIFF` | MIME sniffing | `True` |
| `X_FRAME_OPTIONS` | Clickjacking | `'DENY'` |
| `SECURE_HSTS_SECONDS` | Force HTTPS in browser | `31536000` (1 year) |

---

## Related Documentation

- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [Render Environment Variables](https://render.com/docs/environment-variables)
- [OWASP Security Headers](https://owasp.org/www-project-secure-headers/)

---

**Last Updated:** December 5, 2025  
**Status:** ✅ Production Ready

