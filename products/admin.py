from django.contrib import admin

from products.models import Product, Category, Type

from import_export.admin import ImportExportModelAdmin

# Register your models here.
@admin.register(Category)
class CategoryAdmin(ImportExportModelAdmin):
    list_display = ['name', 'id']
    ordering = ['name',]


@admin.register(Type)
class TypeAdmin(ImportExportModelAdmin):
    list_display = ['name', 'id']
    ordering = ['name',]


@admin.register(Product)
class ProductAdmin(ImportExportModelAdmin):
    list_display = ['sku', 'description', 'category']
    list_filter = ['category']
    ordering = ['category_id',]