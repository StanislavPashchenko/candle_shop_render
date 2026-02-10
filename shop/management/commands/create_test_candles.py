import base64
import os
import random
from decimal import Decimal

from django.db import models
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from shop.models import Candle, Category


_PLACEHOLDER_PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO5fG0cAAAAASUVORK5CYII="
)


class Command(BaseCommand):
    help = 'Создает тестовые свечки (по умолчанию 10)'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=10)
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Удалить существующие свечки перед созданием тестовых данных',
        )

    def handle(self, *args, **options):
        count = int(options['count'])
        if count <= 0:
            raise CommandError('--count должен быть > 0')

        if options.get('reset'):
            Candle.objects.all().delete()

        categories = list(Category.objects.all().order_by('order', 'name'))
        if not categories:
            raise CommandError(
                'Категории не найдены. Сначала добавь категории (например миграцией 0012) и выполни migrate.'
            )

        # ensure media subdir exists on filesystem for local storage backends
        candles_dir_fs = os.path.join(settings.MEDIA_ROOT or '', 'candles')
        os.makedirs(candles_dir_fs, exist_ok=True)

        placeholder_storage_path = 'candles/placeholder.png'

        if not default_storage.exists(placeholder_storage_path):
            png_bytes = base64.b64decode(_PLACEHOLDER_PNG_BASE64)
            default_storage.save(placeholder_storage_path, ContentFile(png_bytes))

        scents = [
            ('Троянда', 'Роза'),
            ('Лавандовий', 'Лавандовый'),
            ('Яблуко', 'Яблоко'),
            ('Апельсин', 'Апельсин'),
            ('Ваніль', 'Ваниль'),
            ('Шоколад', 'Шоколад'),
            ('Морський бриз', 'Морской бриз'),
            ('Мускус', 'Мускус'),
            ('Кардамон', 'Кардамон'),
            ('Корица', 'Корица'),
        ]

        start_order = (Candle.objects.aggregate(max_order=models.Max('order')).get('max_order') or 0) + 1

        created = 0
        for i in range(count):
            scent_uk, scent_ru = random.choice(scents)
            category = random.choice(categories)

            name_uk = f'{scent_uk} свічка test #{i + 1}'
            name_ru = f'{scent_ru} свеча test #{i + 1}'

            price = Decimal(str(random.uniform(80, 300))).quantize(Decimal('0.01'))

            candle = Candle.objects.create(
                name=name_uk,
                name_ru=name_ru,
                description=f'Тестова свічка з ароматом {scent_uk}.',
                description_ru=f'Тестовая свеча с ароматом {scent_ru}.',
                price=price,
                image=placeholder_storage_path,
                category=category,
                order=start_order + i,
                is_hit=False,
                is_on_sale=False,
                discount_percent=None,
            )
            created += 1
            self.stdout.write(f'Создана свеча: {candle.name} ({category.display_name()})')

        self.stdout.write(self.style.SUCCESS(f'✓ Успешно создано {created} тестовых свечек'))
