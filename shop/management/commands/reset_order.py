from django.core.management.base import BaseCommand
from shop.models import Candle


class Command(BaseCommand):
    help = 'Reset order field to 0 for all candles'

    def handle(self, *args, **options):
        count = Candle.objects.all().update(order=0)
        self.stdout.write(self.style.SUCCESS(f'✓ Updated {count} candles: order set to 0'))
