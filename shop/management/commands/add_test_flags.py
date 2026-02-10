from django.core.management.base import BaseCommand
from shop.models import Candle

class Command(BaseCommand):
    help = 'Добавляет хит и скидки на первые товары для тестирования сортировки'

    def handle(self, *args, **options):
        candles = Candle.objects.all()
        
        # Первые 3 товара: хит + скидка
        for candle in candles[:3]:
            candle.is_hit = True
            candle.is_on_sale = True
            candle.discount_percent = 20
            candle.save()
            self.stdout.write(f'✓ {candle.display_name()}: хит + скидка 20%')
        
        # Следующие 3 товара: только скидка
        for candle in candles[3:6]:
            candle.is_hit = False
            candle.is_on_sale = True
            candle.discount_percent = 15
            candle.save()
            self.stdout.write(f'✓ {candle.display_name()}: скидка 15%')
        
        # Следующие 3 товара: только хит
        for candle in candles[6:9]:
            candle.is_hit = True
            candle.is_on_sale = False
            candle.discount_percent = None
            candle.save()
            self.stdout.write(f'✓ {candle.display_name()}: хит')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Успешно добавлены тестовые флаги для проверки сортировки'))
