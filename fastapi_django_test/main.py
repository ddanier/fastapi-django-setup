import os

import django

from .fastapi import get_fastapi_app

# Setup Django - this needs to be done first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastapi_django_test.settings')
django.setup(set_prefix=False)

# Then build FastAPI app, including Django (see fastapi.py)
app = get_fastapi_app()
