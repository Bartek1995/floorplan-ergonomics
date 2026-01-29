"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    root_env = Path(__file__).resolve().parent.parent.parent / '.env'
    local_env = Path(__file__).resolve().parent.parent / '.env'
    if root_env.exists():
        load_dotenv(root_env)
    elif local_env.exists():
        load_dotenv(local_env)
except ImportError:
    pass  # python-dotenv not installed, env vars must be set manually

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_config.settings')

application = get_wsgi_application()
