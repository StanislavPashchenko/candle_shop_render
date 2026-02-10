from django.core.management.base import BaseCommand, CommandError
from shop.models import Category, Candle
from decimal import Decimal
import random
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Создает 10 тестовых категорий и 50 тестовых товаров'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Удалить существующие категории и товары перед созданием тестовых данных',
        )

    def handle(self, *args, **options):
        if options.get('reset'):
            Category.objects.all().delete()
            Candle.objects.all().delete()

        candles_dir = os.path.join(settings.MEDIA_ROOT, 'candles')
        image_candidates = []
        try:
            for filename in os.listdir(candles_dir):
                lower = filename.lower()
                if lower.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                    image_candidates.append(f'candles/{filename}')
        except Exception:
            image_candidates = []

        if not image_candidates:
            raise CommandError(
                'Не найдено ни одного файла изображения в media/candles/. '
                'Добавь туда хотя бы одну картинку (.jpg/.png) и запусти команду снова.'
            )
        
        # Данные для категорий
        categories_data = [
            {
                'name': 'Квітучі свічки',
                'name_ru': 'Цветочные свечи',
                'description': 'Свічки з квітковими ароматами'
            },
            {
                'name': 'Ароматні свічки',
                'name_ru': 'Ароматические свечи',
                'description': 'Свічки з екзотичними запахами'
            },
            {
                'name': 'Фруктові свічки',
                'name_ru': 'Фруктовые свечи',
                'description': 'Свічки з фруктовими ароматами'
            },
            {
                'name': 'Деревні свічки',
                'name_ru': 'Древесные свечи',
                'description': 'Свічки з деревяними нотками'
            },
            {
                'name': 'Специевідні свічки',
                'name_ru': 'Пряные свечи',
                'description': 'Свічки з запахом спецій'
            },
            {
                'name': 'Солодкі свічки',
                'name_ru': 'Сладкие свечи',
                'description': 'Свічки з цукровою ароматом'
            },
            {
                'name': 'Свіжі свічки',
                'name_ru': 'Свежие свечи',
                'description': 'Свічки з бадьорливим запахом'
            },
            {
                'name': 'Класичні свічки',
                'name_ru': 'Классические свечи',
                'description': 'Свічки із традиційними ароматами'
            },
            {
                'name': 'Морські свічки',
                'name_ru': 'Морские свечи',
                'description': 'Свічки з морськими запахами'
            },
            {
                'name': 'Восковані свічки',
                'name_ru': 'Премиум свечи',
                'description': 'Свічки преміум якості'
            }
        ]
        
        # Создаем категории
        categories = []
        for cat_data in categories_data:
            cat, _created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data,
            )
            categories.append(cat)
            self.stdout.write(f'Создана категория: {cat.name}')
        
        # Создаем товары
        scents = [
            ('Троянда', 'Роза'),
            ('Лавандовий', 'Лавандовый'),
            ('Яблуко', 'Яблоко'),
            ('Апельсин', 'Апельсин'),
            ('Ваніль', 'Ваниль'),
            ('Шоколад', 'Шоколад'),
            ('Кавуни', 'Арбуз'),
            ('Ліс', 'Лес'),
            ('Морський бриз', 'Морской бриз'),
            ('Мускус', 'Мускус'),
            ('Кардамон', 'Кардамон'),
            ('Корица', 'Корица'),
            ('Мед', 'Мёд'),
            ('Жасмін', 'Жасмин'),
            ('Лимон', 'Лимон'),
        ]
        
        order = 0
        for i in range(50):
            category = random.choice(categories)
            scent_uk, scent_ru = random.choice(scents)
            
            name_uk = f'{scent_uk} свічка #{i+1}'
            name_ru = f'{scent_ru} свеча #{i+1}'
            description_uk = f'Красива ароматна свічка з запахом {scent_uk}. Від Iris Aroma.'
            description_ru = f'Красивая ароматная свеча с запахом {scent_ru}. От Iris Aroma.'
            
            price = Decimal(str(random.uniform(50, 500)))
            price = price.quantize(Decimal('0.01'))
            
            is_hit = random.choice([True, False, False, False])  # 25% chance
            is_on_sale = random.choice([True, False, False, False])  # 25% chance
            discount_percent = random.randint(5, 30) if is_on_sale else None
            
            candle = Candle.objects.create(
                name=name_uk,
                name_ru=name_ru,
                description=description_uk,
                description_ru=description_ru,
                price=price,
                image=random.choice(image_candidates),
                category=category,
                order=order,
                is_hit=is_hit,
                is_on_sale=is_on_sale,
                discount_percent=discount_percent
            )
            order += 1
            self.stdout.write(f'Создан товар: {candle.name} ({candle.category.name})')
        
        self.stdout.write(self.style.SUCCESS(f'✓ Успешно создано 10 категорий и 50 товаров'))
