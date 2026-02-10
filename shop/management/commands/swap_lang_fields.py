from django.core.management.base import BaseCommand, CommandError
from shop.models import Candle, Category
import uuid

class Command(BaseCommand):
    help = 'Show or swap language fields between primary (uk) and ru fields for Candle and Category.'

    def add_arguments(self, parser):
        parser.add_argument('--apply', action='store_true', help='Apply swap. Without --apply operates in dry-run (report) mode.')
        parser.add_argument('--models', nargs='*', choices=['candle','category'], default=['candle','category'], help='Models to process')
        parser.add_argument('--auto', action='store_true', help='Auto-swap only records that look swapped by language detection (safe).')

    def handle(self, *args, **options):
        apply = options['apply']
        models = options['models']

        if 'category' in models:
            self.stdout.write('Checking Category records...')
            cats = Category.objects.all()
            for c in cats:
                uk = c.name or ''
                ru = c.name_ru or ''
                if uk and ru:
                    if uk == ru:
                        status = 'same'
                    else:
                        status = 'both'
                elif uk and not ru:
                    status = 'uk_only'
                elif ru and not uk:
                    status = 'ru_only'
                else:
                    status = 'empty'
                self.stdout.write(f'Category {c.pk}: uk[{uk[:40]}] ru[{ru[:40]}] -> {status}')
            if apply:
                confirm = input('Apply swap for Category (swap `name` <-> `name_ru`)? [y/N]: ')
                if confirm.lower() == 'y':
                    # Two-phase swap to avoid UNIQUE constraint collisions on `name`.
                    # Phase 1: set temporary unique names for all categories
                    backups = {}
                    for c in cats:
                        backups[c.pk] = (c.name or '', c.name_ru or '')
                        tmp = f"__swap_tmp__{c.pk}__{uuid.uuid4().hex}"
                        c.name = tmp
                        c.save()
                    # Phase 2: assign swapped values
                    for c in cats:
                        old_name, old_name_ru = backups[c.pk]
                        c.name = old_name_ru or ''
                        c.name_ru = old_name or ''
                        c.save()
                    self.stdout.write(self.style.SUCCESS('Categories swapped.'))
                else:
                    self.stdout.write('Skipping Category swap.')

        if 'candle' in models:
            self.stdout.write('\nChecking Candle records...')
            candles = Candle.objects.all()
            for c in candles:
                uk = c.name or ''
                ru = c.name_ru or ''
                duk = c.description or ''
                dru = c.description_ru or ''
                self.stdout.write(f'Candle {c.pk}: name uk[{uk[:40]}] ru[{ru[:40]}]; desc uk[{duk[:40]}] ru[{dru[:40]}]')
            if apply:
                confirm = input('Apply swap for Candle (swap `name`<->`name_ru` and `description`<->`description_ru`)? [y/N]: ')
                if confirm.lower() == 'y':
                    # For candles we can swap safely per-record (no unique constraint on name)
                    for c in candles:
                        new_name = c.name_ru or ''
                        new_name_ru = c.name or ''
                        new_desc = c.description_ru or ''
                        new_desc_ru = c.description or ''
                        c.name = new_name
                        c.name_ru = new_name_ru
                        c.description = new_desc
                        c.description_ru = new_desc_ru
                        c.save()
                    self.stdout.write(self.style.SUCCESS('Candles swapped.'))
                else:
                    self.stdout.write('Skipping Candle swap.')

        # Auto-swap: detect swapped records by simple language heuristics and swap only those
        if options.get('auto'):
            def detect_lang(s: str):
                s = s or ''
                # Ukrainian-specific letters: іїєґ
                if any(ch in s for ch in 'іїєґІЇЄҐ'):
                    return 'uk'
                # Russian-specific letters: ыэё
                if any(ch in s for ch in 'ыэёЫЭЁ'):
                    return 'ru'
                return None

            # Categories: swap only where both fields present and look swapped
            swap_count = 0
            for c in cats:
                if not (c.name and c.name_ru):
                    continue
                lang_name = detect_lang(c.name)
                lang_name_ru = detect_lang(c.name_ru)
                if lang_name == 'ru' and lang_name_ru == 'uk':
                    # safe to swap per-record
                    c.name, c.name_ru = (c.name_ru or ''), (c.name or '')
                    c.save()
                    swap_count += 1
            if swap_count:
                self.stdout.write(self.style.SUCCESS(f'Auto-swapped {swap_count} Category records.'))
            else:
                self.stdout.write('No Category records detected for auto-swap.')

            # Candles: similar detection
            swap_count = 0
            for c in candles:
                if not (c.name and c.name_ru):
                    continue
                lang_name = detect_lang(c.name)
                lang_name_ru = detect_lang(c.name_ru)
                if lang_name == 'ru' and lang_name_ru == 'uk':
                    c.name, c.name_ru = (c.name_ru or ''), (c.name or '')
                    c.description, c.description_ru = (c.description_ru or ''), (c.description or '')
                    c.save()
                    swap_count += 1
            if swap_count:
                self.stdout.write(self.style.SUCCESS(f'Auto-swapped {swap_count} Candle records.'))
            else:
                self.stdout.write('No Candle records detected for auto-swap.')

        self.stdout.write('\nDone. (dry-run if --apply not provided)')
