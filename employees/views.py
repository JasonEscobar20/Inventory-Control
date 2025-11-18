from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView, CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseNotAllowed
from datetime import datetime


from employees.models import Employee
from geo.models import UserProfile
import tablib


class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    fields = '__all__'
    template_name = 'employees/create.html'
    success_url = reverse_lazy('employees:employees_list')

    def form_valid(self, form):
        profile = getattr(self.request.user, 'profile', None)
        if profile and profile.country:
            form.instance.country = profile.country
        return super().form_valid(form)


class EmployeeListView(LoginRequiredMixin, ListView):
    template_name = 'employees/list.html'
    context_object_name = 'employees'
    ordering = ('id',)

    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        qs = Employee.objects.filter(active=True)
        if profile and profile.country:
            qs = qs.filter(country=profile.country)
        return qs
    
    


class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Employee
    fields = '__all__'
    template_name = 'employees/update.html'
    success_url = reverse_lazy('employees:employees_list')

    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        if profile and profile.country:
            return Employee.objects.filter(active=True, country=profile.country)
        return Employee.objects.filter(active=True)


@login_required
def export_employees(request):
    """
    Exporta el listado de colaboradores.
    Soporta los formatos: xlsx (por defecto) y csv via query param ?format=

    Columnas: Código, Nombres, Apellidos
    """
    export_format = request.GET.get('format', 'xlsx').lower()
    if export_format not in ('xlsx', 'csv'):
        export_format = 'xlsx'

    # Preparar dataset
    dataset = tablib.Dataset(headers=['Código', 'Nombres', 'Apellidos'])
    qs = Employee.objects.filter(active=True)
    profile = getattr(request.user, 'profile', None)
    if profile and profile.country:
        qs = qs.filter(country=profile.country)
    for e in qs.order_by('last_name', 'first_name'):
        dataset.append([e.code, e.first_name, e.last_name])

    today = datetime.now().strftime('%Y%m%d')
    filename = f'colaboradores_{today}.{"csv" if export_format == "csv" else "xlsx"}'

    if export_format == 'csv':
        content = dataset.export('csv')
        content_type = 'text/csv; charset=utf-8'
    else:
        content = dataset.export('xlsx')
        content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    response = HttpResponse(content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
def delete_employee(request, pk):
    """Soft delete: marca el empleado como inactivo (active=False)."""
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    profile = getattr(request.user, 'profile', None)
    base_qs = Employee.objects.all()
    if profile and profile.country:
        base_qs = base_qs.filter(country=profile.country)
    employee = get_object_or_404(base_qs, pk=pk)
    if employee.active:
        employee.active = False
        employee.save(update_fields=['active'])

    return redirect('employees:employees_list')