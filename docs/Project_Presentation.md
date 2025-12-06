# E-Commerce Backend - Project Briefing

- **Project Overview**
  - Full e-commerce REST API spanning catalog discovery, cart orchestration, checkout, payments, notifications, and post-purchase care (`README_COMPLETE.md`).
  - Six Django apps, 23 models, and 40+ endpoints cover authentication, users, products, carts, orders, payments, and messaging (`DOCUMENTATION_INDEX.md`).
  - JWT auth with refresh/blacklist flow, environment-aware settings, and Redis/LocMem caching yield 7× faster ORM queries plus 30× faster cached responses (`SUBMISSION_REPORT.md`, `ANALYSIS.md`).
  - Production readiness proven through automated tests, `manage.py check`, semantic commit policy, `FINAL_CHECKLIST.md`, and Render deployment serving static/media via WhiteNoise + object storage.
  - Business KPIs (conversion, payment success, notification delivery) surface in admin dashboards using aggregated analytics endpoints.

- **ERD & Data Model Rationale**
  - Custom `User` inherits from `AbstractBaseUser`, stores marketing preferences + MFA flags, and links to `Address`, `Wishlist`, and `Notification` for personalization (see `ANALYSIS.md`).
  - Catalog uses `Category` trees with slug queries, `Product` metadata, `ProductVariant` for SKU/price/inventory, and `ProductImage` ordering to support localized pricing and media sets.
  - `Cart` aggregates `CartItem` rows per user; `Order` snapshots pricing, tax, shipping, and discounts to retain immutable audit history.
  - `Payment` stores provider enum, intent/client secret, status trail, and failure reasons, while `Notification` tracks template, channel, and send timestamps.
  - Referential integrity relies on `PROTECT`/`CASCADE`, soft deletes, audit columns, and nine composite indexes that accelerate lookups like `(category, is_active)` and `(user, status)`.
  - Signals denormalize cart totals and product ratings into cached fields to avoid repetitive joins on hot paths.

- **Key Endpoints & Features**
  - Authentication endpoints (login/refresh/verify/logout) issue rotating JWTs, enforce blacklisting, and record device metadata for session insights (`README_COMPLETE.md`).
  - Catalog endpoint `GET /api/v1/products/?category=electronics&price_max=500&ordering=-rating` layers search, filtering, ordering, pagination, caching, and `select_related` optimization.
  - Cart endpoints run inside atomic transactions, adjust inventory via `F()` expressions, and trigger Celery alerts for low-stock scenarios.
  - Order creation applies promotion strategies, computes taxes/shipping, reserves inventory, snapshots addresses, and emits `OrderCreated`/`OrderPaid` notifications.
  - Payment endpoints manage Stripe intents, retain client secrets, validate webhooks at `/payments/stripe/webhook/`, and reconcile status with orders.
  - Notification API exposes per-user delivery history while Celery workers fan out via email/SMS providers configured in `notifications/backends.py`.
  - docs: `GET /api/docs/` + `GET /api/schema/` auto-refresh; `/healthz`, `/ready`, `/startup` endpoints power probes; structured logging streams JSON for ingestion.
  - Sample CURL commands and Postman collection reside in `README_COMPLETE.md`, `SUBMISSION_REPORT.md`, and `/docs/assets/postman_collection.json`.

- **Tools, Frameworks & Best Practices**
  - Core stack: Django 5.2, DRF 3.16, drf-spectacular, Celery, Redis, Stripe SDK, django-redis/LocMem cache, WhiteNoise, cloud storage, and Sentry.
  - Productivity: `scripts/seed_data.py`, `Makefile` + `invoke` helpers, `pytest` + coverage, and `pre-commit` hooks standardize lint/test/build flows.
  - Performance: `select_related/prefetch_related`, reusable pagination mixins, multi-layer caching, cache warmers, throttled webhooks, and query profiling captured in `ANALYSIS.md`.
  - Security: rotating JWT refresh tokens, DRF throttles, HTTPS-aware proxy headers, strict CSP/CORS, secrets from `.env`/Render dashboard, and audit logging for sensitive actions.
  - Process: semantic branches (`feat/cart`), branch protection, `GIT_COMMIT_WORKFLOW.md`, `FINAL_CHECKLIST.md`, `PROJECT_COMPLETION_SUMMARY.md`, and automated schema sync keep delivery predictable.
  - Testing: unit + integration coverage for serializers, views, signals, Celery tasks using `pytest --ds=config.settings.test` with in-memory cache + SQLite.

- **Deployment Summary**
  - Runbooks (`RUN_INSTRUCTIONS.md`, `DEPLOYMENT_SUMMARY.md`, `DEPLOYMENT_GUIDE_VISUAL.md`) document local setup, Docker Compose flows, secrets injection, migrations, and static/media routines.
  - `config.settings.production` toggles DATABASE_URL, CACHE_URL, storage backend, logging format, and DEBUG/ALLOWED_HOSTS via `DJANGO_ENV` switch.
  - CI/CD-ready workflow (GitHub Actions) runs tests, builds Docker images, pushes to a registry, and triggers Render deploy hooks, with manual verification for migrations, collectstatic, and superuser creation.
  - Observability relies on `/healthz`, `/ready`, `/startup`, structured JSON logs, Sentry tracing, and Celery beat jobs for housekeeping tasks.
  - Public demo lives at `https://ecommerce-backend-1-v60x.onrender.com`; admin credentials are vaulted, and DRF docs plus sample data ship for demos.

- **Next Steps & References**
  - Feature roadmap: promotion/discount engine, multi-warehouse inventory, subscription products, analytics event stream, and customer support portal.
  - Operations: managed Redis for cache + Celery, dedicated worker/beat deploys, production email/SMS providers (SendGrid/Twilio), and Sentry/APM dashboards.
  - Compliance/resilience: GDPR/CCPA export endpoints, rate-limit dashboards, chaos testing for payment paths, blue/green deployment strategy.
  - Reference set: architecture + metrics (`SUBMISSION_REPORT.md`), endpoint usage (`README_COMPLETE.md`, `/docs/assets/postman_collection.json`), deployment walkthroughs (`RUN_INSTRUCTIONS.md`, `DEPLOYMENT_GUIDE_VISUAL.md`), verification artifacts (`FINAL_CHECKLIST.md`, `PROJECT_COMPLETION_SUMMARY.md`).
