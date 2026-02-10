from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from decimal import Decimal
from django.utils.text import slugify
import requests
import random

from shop.models import Candle, Category


SAMPLE_CATEGORIES = {
    'Ваниль': ['Ванильная классика', 'Ванильный мусс', 'Ванильный кекс', 'Кокосовая ваниль'],
    'Лаванда': ['Прованская лаванда', 'Лавандовое поле', 'Лавандовый час', 'Чистая лаванда'],
    'Шоколад': ['Темный шоколад', 'Шоколадный мусс', 'Шоколадно-апельсиновый', 'Бельгийский шоколад'],
    'Цветы': ['Роза и персик', 'Лотос', 'Жасмин', 'Пион и мусс'],
    'Фрукты': ['Клубника', 'Лимон и мята', 'Мандариновый закат', 'Груша и ваниль'],
    'Дерево': ['Сандаловое дерево', 'Кедр', 'Палисандр', 'Ебеновое дерево'],
    'Специи': ['Корица и гвоздика', 'Имбирь и мускатный орех', 'Анис', 'Кардамон'],
    'Травы': ['Мята и базилик', 'Розмарин', 'Тимьян', 'Шалфей'],
}

ADJECTIVES = ['Нежная', 'Волшебная', 'Тайная', 'Дикая', 'Золотая', 'Серебряная', 'Светлая', 'Мягкая', 'Теплая', 'Холодная']
SUFFIXES = ['Мечты', 'Атмосфера', 'Магия', 'Аромат', 'Парфюм', 'Стиль', 'Гармония', 'Чувство', 'Вибрация', 'Энергия']


class Command(BaseCommand):
    help = 'Create placeholder Candle objects (with images from picsum.photos)'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100, help='How many placeholder items to create')

    def handle(self, *args, **options):
        count = options.get('count', 100) or 100
        
        # Create or get categories
        categories = {}
        for cat_name, variants in SAMPLE_CATEGORIES.items():
            cat, _ = Category.objects.get_or_create(name=cat_name, defaults={'description': f'Категория: {cat_name}'})
            categories[cat_name] = cat
        self.stdout.write(self.style.SUCCESS(f'Categories ready: {len(categories)}'))
        
        created = 0
        category_list = list(categories.values())
        
        for i in range(1, count + 1):
            # Pick category and variant name
            cat_name = random.choice(list(SAMPLE_CATEGORIES.keys()))
            variant = random.choice(SAMPLE_CATEGORIES[cat_name])
            category = categories[cat_name]
            
            # Generate title with adjective
            adjective = random.choice(ADJECTIVES)
            suffix = random.choice(SUFFIXES)
            title = f'{adjective} {variant} — {suffix}'
            
            # Price and description
            price = Decimal(random.choice([79, 99, 129, 149, 179, 199, 249, 299]))
            desc = f'Высококачественная свеча № {i} с ароматом "{variant}". Идеальна для создания уютной атмосферы. Тестовый импорт.'
            
            # Create candle
            c = Candle(
                name=title[:200],
                description=desc,
                price=price,
                category=category,
                order=i,
                is_hit=i <= 6,  # First 6 are hits
                is_on_sale=random.choice([True, False]) and i > 10,  # Random sales after 10
                discount_percent=random.choice([10, 15, 20, 25]) if random.random() > 0.7 else None
            )

            # Fetch placeholder image
            try:
                seed = slugify(f'{cat_name}-{i}')
                img_url = f'https://picsum.photos/seed/{seed}/800/600'
                r = requests.get(img_url, timeout=15)
                r.raise_for_status()
                content = r.content
                if content:
                    fname = f'{seed}.jpg'
                    c.image.save(fname, ContentFile(content), save=False)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Image error for {title}: {e}'))
                pass

            c.save()
            created += 1
            if i % 10 == 0:
                self.stdout.write(self.style.SUCCESS(f'Created: {created} items...'))

        self.stdout.write(self.style.SUCCESS(f'✓ Done — created {created} placeholder products.'))
