from .models import Category

def categories(request):
    """Context processor to add all categories to every template"""
    return {
        'all_categories': Category.objects.all().order_by('order', 'name')
    }
