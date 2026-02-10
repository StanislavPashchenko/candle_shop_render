from django.urls import path
from .views import home, product_list, product_detail, add_to_cart, cart_view, update_cart, checkout, get_nova_poshta_warehouses, privacy_policy

urlpatterns = [
    path('', home, name='home'),
    path('products/', product_list, name='product_list'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('privacy/', privacy_policy, name='privacy_policy'),
    path('cart/add/', add_to_cart, name='cart_add'),
    path('cart/', cart_view, name='cart_view'),
    path('cart/update/', update_cart, name='cart_update'),
    path('checkout/', checkout, name='checkout'),
    path('api/nova-poshta-warehouses/', get_nova_poshta_warehouses, name='nova_poshta_warehouses'),
]
