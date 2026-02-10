from django.core.management.base import BaseCommand
from shop.models import Candle

class Command(BaseCommand):
    help = 'Убирает флаг "хит продаж" и скидки со всех товаров'

    def handle(self, *args, **options):
        # Обновляем все товары
        updated = Candle.objects.all().update(
            is_hit=False,
            is_on_sale=False,
            discount_percent=None
        )
        
        self.stdout.write(self.style.SUCCESS(f'✓ Успешно обновлено {updated} товаров'))
        self.stdout.write('✓ Флаг "хит продаж" - удален')
        self.stdout.write('✓ Скидки - удалены')
