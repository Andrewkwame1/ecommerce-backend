"""
Vercel serverless entry point for the Django app.

Vercel's Python runtime looks for a WSGI/ASGI callable exported from a file in
`api/`. Django itself is unchanged - this file only puts the project root on
`sys.path` (because this file lives in `api/`) and hands Vercel the WSGI app.
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Serverless deployments always use production settings.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

from config.wsgi import application  # noqa: E402

# Vercel detects `app` for WSGI applications.
app = application
