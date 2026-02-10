from django.core.management.base import BaseCommand
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.utils.text import slugify
from decimal import Decimal
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import random

from shop.models import Candle


class Command(BaseCommand):
    help = 'Import sample candles from irisaroma.com (for testing).'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=10, help='Number of products to import')
        parser.add_argument('--source', type=str, default='https://irisaroma.com/aromasvichky/', help='Source URL')
        parser.add_argument('--debug', action='store_true', help='Dump debug info')

    def handle(self, *args, **options):
        limit = options['limit']
        src = options['source']
        self.stdout.write(f'Fetching product list from {src} ...')

        try:
            resp = requests.get(src, timeout=20)
            resp.raise_for_status()
        except Exception as e:
            raise Exception(f'Failed to fetch {src}: {e}')

        soup = BeautifulSoup(resp.text, 'html.parser')

        # Try several selectors to find product tiles
        candidates = []
        selectors = [
            '.products .product',
            '.product',
            '.post',
            '.item',
            'article',
            '.woocommerce-LoopProduct-link',
            '.portfolio-item',
            '.product-type-simple',
            '.product-card',
            '.product-item',
        ]

        for sel in selectors:
            found = soup.select(sel)
            if found and len(found) >= 1:
                candidates = found
                break

        # Fallback: all links with images (common in many shops)
        if not candidates:
            for a in soup.find_all('a'):
                if a.find('img'):
                    candidates.append(a)

        # debug info: counts per selector
        if options.get('debug'):
            self.stdout.write('Selector debug counts:')
            for sel in selectors:
                try:
                    cnt = len(soup.select(sel))
                except Exception:
                    cnt = 0
                self.stdout.write(f'  {sel}: {cnt}')
            # also dump first 3000 chars of page to a file for inspection
            try:
                with open('irisaroma_debug.html', 'w', encoding='utf-8') as f:
                    f.write(resp.text[:300000])
                self.stdout.write(self.style.WARNING('Wrote irisaroma_debug.html (first 300k chars)'))
            except Exception as e:
                self.stderr.write(f'Failed to write debug html: {e}')

        self.stdout.write(f'Found {len(candidates)} candidate nodes')

        added = 0
        seen = set()

        for node in candidates:
            if added >= limit:
                break


            # extract name
            title = None
            # try heading tags first
            for h in ('h1', 'h2', 'h3', 'h4', 'h5'):
                t = node.find(h)
                if t and t.get_text(strip=True):
                    title = t.get_text(strip=True)
                    break

            # try common title classes
            if not title:
                for cls in ('entry-title', 'post-title', 'product-title', 'woocommerce-loop-product__title', 'title', 'name'):
                    t = node.select_one('.' + cls)
                    if t and t.get_text(strip=True):
                        title = t.get_text(strip=True)
                        break

            # try image alt attribute
            if not title:
                img_tag_tmp = node.find('img')
                if img_tag_tmp and img_tag_tmp.get('alt'):
                    title = img_tag_tmp.get('alt').strip()

            # maybe the link text or node text
            if not title:
                title = node.get_text(strip=True)[:120]

            if not title:
                continue

            if title in seen:
                continue
            seen.add(title)

            # image
            img_tag = node.find('img') or (node if node.name == 'img' else None)
            img_url = None
            if img_tag:
                img_url = img_tag.get('data-src') or img_tag.get('src') or img_tag.get('data-lazy-src')
                if img_url:
                    img_url = urljoin(src, img_url)

            # Try to get detailed description by following link
            desc = ''
            aroma = ''
            link = None
            a_tag = node.find('a') if node.find('a') else (node if node.name == 'a' else None)
            if a_tag and a_tag.get('href'):
                link = urljoin(src, a_tag.get('href'))
            elif node.get('href'):
                link = urljoin(src, node.get('href'))

            if link:
                try:
                    r2 = requests.get(link, timeout=15)
                    r2.raise_for_status()
                    s2 = BeautifulSoup(r2.text, 'html.parser')
                    # find description
                    p = s2.find('div', class_='entry') or s2.find('div', class_='post-content') or s2.find('div', class_='product')
                    if p:
                        desc = p.get_text(separator=' ', strip=True)[:2000]
                    # try get large image
                    im2 = s2.find('img')
                    if im2 and im2.get('src'):
                        img_url = urljoin(link, im2.get('src'))
                    # try aroma
                    text = s2.get_text(separator=' ', strip=True)
                    # crude search for words like 'аромат' or 'аром' in Russian/Ukrainian
                    for token in ('Аромат','аромат','Арома','арома','aroma'):
                        if token in text:
                            # take a short substring around token
                            idx = text.find(token)
                            aroma = text[idx:idx+120]
                            break
                except Exception:
                    pass

            # fallback values
            if not desc:
                desc = f'Тестовый импорт: {title}'
            if not aroma:
                aroma = 'Смешанный'

            # price random test value
            price = Decimal(random.choice([99,129,159,189,199,229,259]))

            # create Candle
            try:
                c = Candle()
                c.name = title[:200]
                c.description = desc
                c.price = price
                c.aroma = aroma[:100]

                if img_url:
                    try:
                        img_resp = requests.get(img_url, stream=True, timeout=20)
                        img_resp.raise_for_status()
                        tmp = NamedTemporaryFile(delete=True)
                        for chunk in img_resp.iter_content(1024):
                            tmp.write(chunk)
                        tmp.flush()
                        filename = slugify(title)[:50] or 'img'
                        # guess extension
                        ext = 'jpg'
                        if 'png' in img_url.lower():
                            ext = 'png'
                        fname = f'{filename}.{ext}'
                        c.image.save(fname, File(open(tmp.name, 'rb')))
                    except Exception:
                        # skip image
                        pass

                c.save()
                added += 1
                self.stdout.write(self.style.SUCCESS(f'Added: {c.name}'))
            except Exception as e:
                self.stderr.write(f'Failed to create {title}: {e}')

        self.stdout.write(self.style.SUCCESS(f'Import finished — added {added} products.'))
