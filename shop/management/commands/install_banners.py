from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from pathlib import Path
import requests


class Command(BaseCommand):
    help = 'Download example banner images into MEDIA_ROOT/candles/banner'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=3, help='How many banner images to download')

    def handle(self, *args, **options):
        count = options.get('count', 3)
        media_root = Path(settings.MEDIA_ROOT)
        target = media_root / 'candles' / 'banner'
        target.mkdir(parents=True, exist_ok=True)

        seeds = ['banner1', 'banner2', 'banner3', 'banner4', 'banner5']
        created = 0
        for i in range(count):
            seed = seeds[i % len(seeds)]
            url = f'https://picsum.photos/seed/{seed}/1400/600'
            try:
                r = requests.get(url, timeout=15)
                r.raise_for_status()
                content = r.content
                if not content:
                    self.stderr.write(f'No content for {url}')
                    continue
                fname = f'banner{i+1}.jpg'
                dest = target / fname
                with open(dest, 'wb') as f:
                    f.write(content)
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Wrote {dest}'))
            except Exception as e:
                self.stderr.write(f'Failed to download {url}: {e}')

        self.stdout.write(self.style.SUCCESS(f'Finished. Created {created} banner images in {target}'))
