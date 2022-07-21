from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin


from employees.models import Employee


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    fields = '__all__'
    template_name = 'employees/create.html'
    success_url = reverse_lazy('employees:employees_list')


class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'employees/list.html'
    context_object_name = 'employees'
    ordering = ('id',)


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    fields = '__all__'
    template_name = 'employees/update.html'
    success_url = reverse_lazy('employees:employees_list')