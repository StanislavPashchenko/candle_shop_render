import os
import sys
from pathlib import Path
# ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
print('ENV POSTGRES_DB before import:', os.environ.get('POSTGRES_DB'))
print('ENV POSTGRES_USER before import:', os.environ.get('POSTGRES_USER'))
print('ENV POSTGRES_PASSWORD before import:', os.environ.get('POSTGRES_PASSWORD'))
print('ENV POSTGRES_HOST before import:', os.environ.get('POSTGRES_HOST'))
print('ENV DJANGO_SETTINGS_MODULE before import:', os.environ.get('DJANGO_SETTINGS_MODULE'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings
print('settings.DATABASES =', settings.DATABASES)
