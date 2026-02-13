import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from shop.models import Candle, Category, Collection


class Command(BaseCommand):
    help = 'Импортирует Category/Collection/Candle из старой sqlite БД в текущую БД'

    def add_arguments(self, parser):
        parser.add_argument(
            '--old-db',
            default=str(Path(settings.BASE_DIR) / 'db.sqlite3_old'),
            help='Путь к старой sqlite БД (по умолчанию BASE_DIR/db.sqlite3_old)',
        )
        parser.add_argument(
            '--truncate',
            action='store_true',
            help='Очистить текущие таблицы Candle/Category/Collection перед импортом',
        )
        parser.add_argument(
            '--candle-match',
            choices=['name', 'name_category', 'id'],
            default='name_category',
            help='Как определять, что свеча уже существует и её не нужно импортировать',
        )

    def handle(self, *args, **options):
        old_db_path = Path(options['old_db']).expanduser().resolve()
        if not old_db_path.exists():
            raise CommandError(f'Файл старой БД не найден: {old_db_path}')

        conn = sqlite3.connect(str(old_db_path))
        conn.row_factory = sqlite3.Row

        try:
            old_tables = self._get_tables(conn)
            for required in ('shop_category', 'shop_candle'):
                if required not in old_tables:
                    raise CommandError(
                        f'В старой БД нет таблицы {required}. Найдены: {", ".join(sorted(old_tables))}'
                    )

            category_cols = self._get_columns(conn, 'shop_category')
            candle_cols = self._get_columns(conn, 'shop_candle')
            collection_cols = self._get_columns(conn, 'shop_collection') if 'shop_collection' in old_tables else set()

            with transaction.atomic():
                if options['truncate']:
                    Candle.objects.all().delete()
                    Category.objects.all().delete()
                    Collection.objects.all().delete()

                category_id_map, categories_created, categories_skipped = self._import_categories(conn, category_cols)

                collections_created = 0
                collections_skipped = 0
                collection_id_map = {}
                if 'shop_collection' in old_tables:
                    (
                        collection_id_map,
                        collections_created,
                        collections_skipped,
                    ) = self._import_collections(conn, collection_cols)

                candles_created, candles_skipped = self._import_candles(
                    conn,
                    candle_cols,
                    category_id_map=category_id_map,
                    collection_id_map=collection_id_map,
                    candle_match=options['candle_match'],
                )

            self.stdout.write(self.style.SUCCESS('✓ Импорт завершён'))
            self.stdout.write(
                f'Category: created={categories_created}, skipped_existing={categories_skipped}\n'
                f'Collection: created={collections_created}, skipped_existing={collections_skipped}\n'
                f'Candle: created={candles_created}, skipped_existing={candles_skipped}'
            )

        finally:
            conn.close()

    def _get_tables(self, conn):
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        return {r['name'] for r in rows}

    def _get_columns(self, conn, table):
        rows = conn.execute(f'PRAGMA table_info({table})').fetchall()
        return {r['name'] for r in rows}

    def _qcols(self, cols):
        return ', '.join([f'"{c}"' for c in cols])

    def _import_categories(self, conn, cols):
        select_cols = [c for c in ('id', 'name', 'name_ru', 'description', 'order') if c in cols]
        rows = conn.execute(
            f"SELECT {self._qcols(select_cols)} FROM shop_category ORDER BY \"id\""
        ).fetchall()

        created = 0
        skipped = 0
        id_map = {}
        for r in rows:
            old_id = r['id']
            name = r['name'] if 'name' in r.keys() else None
            if not name:
                continue

            defaults = {
                'name_ru': r['name_ru'] if 'name_ru' in r.keys() else None,
                'description': (r['description'] or '') if 'description' in r.keys() else '',
                'order': (r['order'] or 0) if 'order' in r.keys() else 0,
            }

            obj, was_created = Category.objects.get_or_create(name=name, defaults=defaults)
            if was_created:
                created += 1
            else:
                skipped += 1
            id_map[old_id] = obj.id

        return id_map, created, skipped

    def _import_collections(self, conn, cols):
        select_cols = [
            c
            for c in (
                'id',
                'code',
                'title_uk',
                'title_ru',
                'description_uk',
                'description_ru',
                'description',
                'order',
            )
            if c in cols
        ]
        rows = conn.execute(
            f"SELECT {self._qcols(select_cols)} FROM shop_collection ORDER BY \"id\""
        ).fetchall()

        created = 0
        skipped = 0
        id_map = {}
        for r in rows:
            old_id = r['id']
            code = r['code'] if 'code' in r.keys() else None
            if not code:
                continue

            defaults = {}
            for field in (
                'title_uk',
                'title_ru',
                'description_uk',
                'description_ru',
                'description',
                'order',
            ):
                if field in r.keys():
                    defaults[field] = r[field]

            obj, was_created = Collection.objects.get_or_create(code=code, defaults=defaults)
            if was_created:
                created += 1
            else:
                skipped += 1
            id_map[old_id] = obj.id

        return id_map, created, skipped

    def _import_candles(self, conn, cols, *, category_id_map, collection_id_map, candle_match):
        select_cols = [
            c
            for c in (
                'id',
                'name',
                'name_ru',
                'description',
                'description_ru',
                'price',
                'image',
                'category_id',
                'order',
                'is_hit',
                'is_on_sale',
                'discount_percent',
                'collection_id',
            )
            if c in cols
        ]

        rows = conn.execute(
            f"SELECT {self._qcols(select_cols)} FROM shop_candle ORDER BY \"id\""
        ).fetchall()

        created = 0
        skipped = 0

        for r in rows:
            old_id = r['id']
            name = r['name'] if 'name' in r.keys() else None
            if not name:
                continue

            old_category_id = r['category_id'] if 'category_id' in r.keys() else None
            old_collection_id = r['collection_id'] if 'collection_id' in r.keys() else None

            new_category_id = category_id_map.get(old_category_id) if old_category_id else None
            new_collection_id = collection_id_map.get(old_collection_id) if old_collection_id else None

            if candle_match == 'id':
                if Candle.objects.filter(id=old_id).exists():
                    skipped += 1
                    continue
            elif candle_match == 'name':
                if Candle.objects.filter(name=name).exists():
                    skipped += 1
                    continue
            else:  # name_category
                qs = Candle.objects.filter(name=name)
                if new_category_id is None:
                    qs = qs.filter(category__isnull=True)
                else:
                    qs = qs.filter(category_id=new_category_id)
                if qs.exists():
                    skipped += 1
                    continue

            candle_data = {
                'name': name,
                'name_ru': r['name_ru'] if 'name_ru' in r.keys() else None,
                'description': r['description'] if 'description' in r.keys() else '',
                'description_ru': r['description_ru'] if 'description_ru' in r.keys() else None,
                'price': str(r['price']) if 'price' in r.keys() and r['price'] is not None else '0',
                'image': r['image'] if 'image' in r.keys() else '',
                'category_id': new_category_id,
                'collection_id': new_collection_id,
                'order': (r['order'] or 0) if 'order' in r.keys() else 0,
                'is_hit': bool(r['is_hit']) if 'is_hit' in r.keys() else False,
                'is_on_sale': bool(r['is_on_sale']) if 'is_on_sale' in r.keys() else False,
                'discount_percent': r['discount_percent'] if 'discount_percent' in r.keys() else None,
            }

            obj = Candle.objects.create(**candle_data)
            created += 1

        return created, skipped
