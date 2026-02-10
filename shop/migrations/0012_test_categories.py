from django.db import migrations


def create_test_categories(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')

    categories_data = [
        {
            'name': 'Квітучі свічки',
            'name_ru': 'Цветочные свечи',
            'description': 'Свічки з квітковими ароматами',
            'order': 0,
        },
        {
            'name': 'Ароматні свічки',
            'name_ru': 'Ароматические свечи',
            'description': 'Свічки з екзотичними запахами',
            'order': 1,
        },
        {
            'name': 'Фруктові свічки',
            'name_ru': 'Фруктовые свечи',
            'description': 'Свічки з фруктовими ароматами',
            'order': 2,
        },
        {
            'name': 'Деревні свічки',
            'name_ru': 'Древесные свечи',
            'description': 'Свічки з деревяними нотками',
            'order': 3,
        },
        {
            'name': 'Специевідні свічки',
            'name_ru': 'Пряные свечи',
            'description': 'Свічки з запахом спецій',
            'order': 4,
        },
    ]

    for cat_data in categories_data:
        name = cat_data['name']
        defaults = {k: v for k, v in cat_data.items() if k != 'name'}
        Category.objects.get_or_create(name=name, defaults=defaults)


def remove_test_categories(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    Category.objects.filter(
        name__in=[
            'Квітучі свічки',
            'Ароматні свічки',
            'Фруктові свічки',
            'Деревні свічки',
            'Специевідні свічки',
        ]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_order_payment_method'),
    ]

    operations = [
        migrations.RunPython(create_test_categories, reverse_code=remove_test_categories),
    ]
