from django.urls import path

from inventory_control.api import views

urlpatterns = [
    path('api/list/', views.InventoryList.as_view(), name='api_inventory_list'),
    path('api/create/', views.InventoryCreate.as_view(), name='api_inventory_create'),
    path('api/status/update/<int:pk>/', views.InventoryStatusUpdate.as_view(), name='api_inventory_status_update'),

    ## inventory count
    path('api/count/create/', views.InventoryCountCreate.as_view(), name='api_inventory_count_create' ),
    path('api/counts/list/<int:inventory_id>/', views.InventoryCountList.as_view(), name='api_inventory_counts_list'),
    path('api/count/update/<int:pk>/', views.InventoryCountUpdate.as_view(), name='api_inventory_count_update'),

    path('api/count/filter/', views.InventoryCountFilter.as_view(), name='api_inventory_count_filter'),
    
]