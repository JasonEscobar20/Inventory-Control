from django.urls import path

from products.api.views import ProductCreate, ProductList, ProductFilter


app_name = 'products_api'

urlpatterns = [
    path('api/list/',ProductList.as_view(), name='api_product_list'),
    path('api/create/',ProductCreate.as_view(), name='api_product_create'),
    path('api/filter/',ProductFilter.as_view(), name='api_product_filter' ),
]