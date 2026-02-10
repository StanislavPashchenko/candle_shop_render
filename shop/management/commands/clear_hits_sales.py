from django.core.management.base import BaseCommand
from shop.models import Candle


class Command(BaseCommand):
    help = 'Remove all hits and sales flags from candles'

    def handle(self, *args, **options):
        count = Candle.objects.all().update(is_hit=False, is_on_sale=False, discount_percent=None)
        self.stdout.write(self.style.SUCCESS(f'✓ Updated {count} candles: removed all hits and sales'))
