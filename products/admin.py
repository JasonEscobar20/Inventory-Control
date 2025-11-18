from django.contrib import admin

from products.models import Brand, Product

from import_export.admin import ImportExportModelAdmin


@admin.register(Brand)
class BrandAdmin(ImportExportModelAdmin):
    list_display = ['name', 'country']
    list_filter = ['country']


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ['sku', 'description', 'brand', 'country']
    list_filter = ['country', 'brand']