from django.core.management.base import BaseCommand
from shop.models import Candle

class Command(BaseCommand):
    help = 'Убирает порядок со всех товаров'

    def handle(self, *args, **options):
        # Обновляем все товары
        updated = Candle.objects.all().update(order=0)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Успешно обновлено {updated} товаров'))
        self.stdout.write('✓ Порядок - удален (установлено значение 0 для всех товаров)')
