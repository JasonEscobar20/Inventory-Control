from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from .models import Country, UserProfile


@admin.register(Country)
class CountryAdmin(ImportExportModelAdmin):
    list_display = ['name', 'code']
    ordering = ('name',)


@admin.register(UserProfile)
class UserProfileAdmin(ImportExportModelAdmin):
    list_display = ['user', 'country']
    list_filter = ['country']