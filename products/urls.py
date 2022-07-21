from django.urls import path

from products import views

from products.api.urls import urlpatterns  as api_urls

app_name = 'products'


urlpatterns = [
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('list/', views.ProductListView.as_view(), name='product_list'),

    path('update/<slug:pk>/', views.ProductUpdateView.as_view(), name='product_update')

] + api_urls