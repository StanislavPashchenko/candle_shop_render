from pathlib import Path
import json

# count in data.json
p = Path('data.json')
if p.exists():
    with p.open('r', encoding='utf-8') as f:
        data = json.load(f)
    cnt_candle = sum(1 for o in data if o.get('model') == 'shop.candle')
    cnt_category = sum(1 for o in data if o.get('model') == 'shop.category')
    print('fixture shop.candle:', cnt_candle)
    print('fixture shop.category:', cnt_category)
else:
    print('data.json not found')

# count in DB via Django
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','config.settings')
import django
django.setup()
from shop.models import Candle, Category
print('DB Category.count =', Category.objects.count())
print('DB Candle.count =', Candle.objects.count())
print('Sample candles:')
for c in Candle.objects.all()[:10]:
    print('-', c.id, c.name, c.price)
