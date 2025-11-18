from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from employees.models import Employee, Department
from geo.models import Country


# Register your models here.
@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    list_display = ['first_name', 'last_name', 'country']
    list_filter = ['country']
    ordering = ('id',)
    
    
@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    list_display = ['name']
    ordering = ('id',)