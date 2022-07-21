from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from employees.models import Employee


# Register your models here.
@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    list_display = ['first_name', 'last_name']
    ordering = ('id',)