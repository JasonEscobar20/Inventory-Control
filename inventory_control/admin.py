from django.contrib import admin

from inventory_control.models import (
    Inventory,
    Warehouse,
    StorageType,
    ProductStatus,
    InventoryCount
)
from geo.models import Country

from import_export.admin import ImportExportModelAdmin

# Register your models here.
@admin.register(Warehouse)
class WarehouseAdmin(ImportExportModelAdmin):
    list_display = ['name', 'country']
    list_filter = ['country']


@admin.register(Inventory)
class InventoryAdmin(ImportExportModelAdmin):
    list_display = ['warehouse', 'employee', 'store', 'status', 'country']
    list_filter = ['warehouse', 'employee', 'store', 'status', 'country']


@admin.register(StorageType)
class StorageTypeAdmin(ImportExportModelAdmin):
    list_display = ['name']


@admin.register(ProductStatus)
class ProductStatusAdmin(ImportExportModelAdmin):
    list_display = ['name']


@admin.register(InventoryCount)
class InventoryCountAdmin(ImportExportModelAdmin):
    list_display = ['product', 'amount', 'created', 'creator', 'product_status', 'country']
    list_filter = ['product_status', 'country']