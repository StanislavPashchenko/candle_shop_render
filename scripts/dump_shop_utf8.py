import os
from pathlib import Path
import sys
# ensure project root on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# use SQLite settings to read original DB
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings_sqlite')
import django
from django.core.management import call_command

django.setup()
OUT = Path('data_shop.json')
with OUT.open('w', encoding='utf-8') as f:
    call_command('dumpdata', 'shop', stdout=f, indent=2, natural_foreign=True, natural_primary=True)
print('Wrote', OUT)
