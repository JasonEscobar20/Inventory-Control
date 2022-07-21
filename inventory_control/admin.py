from django.contrib import admin

from inventory_control.models import (
    Inventory,
    Warehouse,
    MeasurementUnit,
    Side,
    StorageType,
    ProductStatus,
    InventoryCount
)

from import_export.admin import ImportExportModelAdmin

# Register your models here.
@admin.register(Warehouse)
class WarehouseAdmin(ImportExportModelAdmin):
    list_display = ['name']


@admin.register(Inventory)
class InventoryAdmin(ImportExportModelAdmin):
    list_display = ['warehouse', 'employee', 'store', 'status']
    list_filter = ['warehouse', 'employee', 'store', 'status']


@admin.register(MeasurementUnit)
class MeasurementUnitAdmin(ImportExportModelAdmin):
    list_display = ['name']


@admin.register(Side)
class SideAdmin(ImportExportModelAdmin):
    list_display = ['name']


@admin.register(StorageType)
class StorageTypeAdmin(ImportExportModelAdmin):
    list_display = ['name']


@admin.register(ProductStatus)
class ProductStatusAdmin(ImportExportModelAdmin):
    list_display = ['name']


@admin.register(InventoryCount)
class InventoryCountAdmin(ImportExportModelAdmin):
    list_display = ['product', 'amount', 'created', 'creator', 'entry_date', 'product_status']
    list_filter = ['product_status', 'measurement_unit']