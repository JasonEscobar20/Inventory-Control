from distutils.log import Log
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, View, UpdateView

from inventory_control.models import Inventory, Warehouse, Employee, MeasurementUnit, ProductStatus, Side, StorageType
from products.models import Product


class SignInView(LoginView):
    template_name = 'login/login.html'
    # success_url = reverse_lazy('notarial_deed:appointment-certificates-view')


class SignOutView(LogoutView):
    pass


class IndexView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        user = self.request.user

        if user.is_authenticated:
            return redirect(reverse_lazy('inventory_control:inventory-control-list'))


class InventoryControlListView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory_control/list.html'

    def get_context_data(self, **kwargs):
        kwargs['products'] = Product.objects.filter(active=True)
        kwargs['measurement_units'] = MeasurementUnit.objects.all()
        kwargs['product_status'] = ProductStatus.objects.all()
        kwargs['sides'] = Side.objects.all()
        kwargs['storage_types'] = StorageType.objects.all()

        return super().get_context_data(**kwargs)



class InventoryControlCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory_control/create.html'

    def get_context_data(self, **kwargs):
        warehouses = Warehouse.objects.all().order_by('id')
        employees = Employee.objects.all().order_by('first_name')

        kwargs['warehouses'] = warehouses
        kwargs['employees'] = employees

        return super().get_context_data(**kwargs)


class InventoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Inventory
    fields = ['warehouse', 'employee', 'store']
    template_name = 'inventory_control/update.html'
    success_url = reverse_lazy('inventory_control:inventory-control-list')

    def get_context_data(self, **kwargs):
        warehouses = Warehouse.objects.all().order_by('id')
        employees = Employee.objects.all().order_by('first_name')
        stores = get_user_model().objects.all()

        kwargs['warehouses'] = warehouses
        kwargs['employees'] = employees
        kwargs['stores'] = stores

        return super().get_context_data(**kwargs)

    
class InventoryCountListView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory_control/counting.html'

    def get_context_data(self, **kwargs):
        last_position_data = {
            'storage_type': 1,
            'storage_position': 1,
            'level': 1,
            'position': 1,
            'side': 1
        }

        inventory_id = kwargs['inventory_id']
        
        inventory_instance = Inventory.objects.get(pk=inventory_id)
        verify_counts = inventory_instance.inventory_records.all()

        if verify_counts.count() > 0:
            last_count = verify_counts.last()
            last_position_data['storage_type'] = last_count.storage_type.id
            last_position_data['storage_position'] = last_count.storage_position
            last_position_data['level'] = last_count.level
            last_position_data['position'] = last_count.position
            last_position_data['side'] = last_count.side.id

        kwargs['last_position'] = last_position_data
        kwargs['products'] = Product.objects.filter(active=True)
        kwargs['measurement_units'] = MeasurementUnit.objects.all()
        kwargs['product_status'] = ProductStatus.objects.all()
        kwargs['sides'] = Side.objects.all()
        kwargs['storage_types'] = StorageType.objects.all()

        return super().get_context_data(**kwargs)