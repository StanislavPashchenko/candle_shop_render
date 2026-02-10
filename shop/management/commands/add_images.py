from django.core.management.base import BaseCommand
from shop.models import Candle
from PIL import Image, ImageDraw, ImageFont
import os
from django.core.files.base import ContentFile
from io import BytesIO
import random

class Command(BaseCommand):
    help = 'Добавляет сгенерированные картинки для всех товаров'

    def handle(self, *args, **options):
        # Цвета для свечей
        colors = [
            '#FF69B4',  # Hot Pink
            '#FFB6C1',  # Light Pink
            '#FFA500',  # Orange
            '#FFD700',  # Gold
            '#FFC0CB',  # Pink
            '#DDA0DD',  # Plum
            '#FF6B9D',  # Red Pink
            '#C71585',  # Medium Violet Red
            '#FF8C00',  # Dark Orange
            '#FFE4B5',  # Moccasin
            '#FFDAB9',  # Peach Puff
            '#F0E68C',  # Khaki
            '#EE82EE',  # Violet
            '#DA70D6',  # Orchid
            '#BA55D3',  # Medium Orchid
            '#9932CC',  # Dark Orchid
            '#8A2BE2',  # Blue Violet
            '#FF00FF',  # Magenta
            '#FF1493',  # Deep Pink
            '#FF69B4',  # Hot Pink
        ]
        
        candles = Candle.objects.all()
        media_path = 'media/candles/'
        
        # Убедиться что папка существует
        os.makedirs(media_path, exist_ok=True)
        
        for i, candle in enumerate(candles):
            # Генерируем картинку
            width, height = 600, 400
            img = Image.new('RGB', (width, height), color=random.choice(colors))
            draw = ImageDraw.Draw(img)
            
            # Добавляем текст
            try:
                # Пытаемся найти системный шрифт
                font_size = 48
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                # Если шрифт не найден, используем стандартный
                font = ImageFont.load_default()
            
            # Текст с названием
            text = candle.display_name()[:30]  # Первые 30 символов
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            draw.text((x, y), text, fill='white', font=font)
            
            # Сохраняем в memory
            img_io = BytesIO()
            img.save(img_io, format='JPEG', quality=85)
            img_io.seek(0)
            
            # Сохраняем файл
            filename = f'candle_{candle.id}.jpg'
            candle.image.save(filename, ContentFile(img_io.read()), save=True)
            
            self.stdout.write(f'✓ {candle.display_name()} - добавлена картинка')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Успешно добавлены картинки для {len(candles)} товаров'))
