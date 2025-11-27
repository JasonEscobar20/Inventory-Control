from django.urls import path

from inventory_control import views
from inventory_control import reports
from inventory_control.api.urls import urlpatterns as api_urls

app_name = 'inventory_control'

urlpatterns = [
    path('login/', views.SignInView.as_view(), name='login-view'),
    path('logout/', views.SignOutView.as_view(), name='logout'),
    path('', views.IndexView.as_view(), name='inventory-index-view'),

    path('list/', views.InventoryControlListView.as_view(), name='inventory-control-list'),
    path('create/', views.InventoryControlCreateView.as_view(), name='inventory-control-create'),
    path('update/<int:pk>/', views.InventoryUpdateView.as_view(), name='inventory-control-update'),

    path('counting/list/<int:inventory_id>/', views.InventoryCountListView.as_view(), name='inventory_count_list'),

    path('generate/inventory_count/report/', reports.InventoryCountReport.as_view()),
] + api_urls