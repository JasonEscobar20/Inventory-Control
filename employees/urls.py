from django.urls import path

from employees import views

app_name = 'employees'

urlpatterns = [
    path('create/', views.EmployeeCreateView.as_view(), name='employee_create'),
    path('list/', views.EmployeeListView.as_view(), name='employees_list'),
    path('download/', views.export_employees, name='employees_download'),
    path('delete/<slug:pk>/', views.delete_employee, name='employee_delete'),

    path('update/<slug:pk>/', views.EmployeeUpdateView.as_view(), name='employee_update')

]