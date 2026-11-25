from distutils.log import Log
import mimetypes
from PIL import Image, UnidentifiedImageError
from django.http import FileResponse
from django.core.exceptions import SuspiciousFileOperation
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, View, UpdateView

from inventory_control.models import Inventory, Warehouse, Employee, ProductStatus, StorageType, InventoryCount
from products.models import Product
from geo.models import UserProfile


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
        profile = getattr(self.request.user, 'profile', None)
        country = getattr(profile, 'country', None)
        product_qs = Product.objects.filter(active=True)
        ps_qs = ProductStatus.objects.all()
        st_qs = StorageType.objects.all()
        if country:
            product_qs = product_qs.filter(country=country)
        kwargs['products'] = product_qs
        kwargs['product_status'] = ps_qs
        kwargs['storage_types'] = st_qs
        # Add warehouses and employees for filters
        warehouses = Warehouse.objects.all().order_by('name')
        employees = Employee.objects.filter(active=True).order_by('first_name')
        if country:
            warehouses = warehouses.filter(country=country)
            employees = employees.filter(country=country)
        kwargs['warehouses'] = warehouses
        kwargs['employees'] = employees

        return super().get_context_data(**kwargs)



class InventoryControlCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory_control/create.html'

    def get_context_data(self, **kwargs):
        profile = getattr(self.request.user, 'profile', None)
        country = getattr(profile, 'country', None)
        warehouses = Warehouse.objects.all().order_by('id')
        employees = Employee.objects.filter(active=True).order_by('first_name')
        if country:
            warehouses = warehouses.filter(country=country)
            employees = employees.filter(country=country)

        kwargs['warehouses'] = warehouses
        kwargs['employees'] = employees

        return super().get_context_data(**kwargs)


class InventoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Inventory
    fields = ['warehouse', 'employee', 'store']
    template_name = 'inventory_control/update.html'
    success_url = reverse_lazy('inventory_control:inventory-control-list')

    def get_queryset(self):
        profile = getattr(self.request.user, 'profile', None)
        country = getattr(profile, 'country', None)
        qs = Inventory.objects.all()
        if country:
            qs = qs.filter(country=country)
        return qs

    def get_context_data(self, **kwargs):
        profile = getattr(self.request.user, 'profile', None)
        country = getattr(profile, 'country', None)
        warehouses = Warehouse.objects.all().order_by('id')
        employees = Employee.objects.filter(active=True).order_by('first_name')
        stores = get_user_model().objects.all()
        if country:
            warehouses = warehouses.filter(country=country)
            employees = employees.filter(country=country)

        kwargs['warehouses'] = warehouses
        kwargs['employees'] = employees
        kwargs['stores'] = stores

        return super().get_context_data(**kwargs)

    
class InventoryCountListView(LoginRequiredMixin, TemplateView):
    template_name = 'inventory_control/counting.html'

    def get_context_data(self, **kwargs):
        last_position_data = {
            'storage_type': 1,
            'position_letter': 'A',
            'level': 1,
            'position': 1,
        }

        inventory_id = kwargs['inventory_id']
        
        inventory_instance = Inventory.objects.get(pk=inventory_id)
        last_count = (
            inventory_instance.inventory_records
            .filter(active=True)
            .order_by('-id')
            .first()
        )

        if last_count:
            last_position_data['storage_type'] = last_count.storage_type_id
            last_position_data['position_letter'] = last_count.position_letter
            last_position_data['level'] = last_count.level
            last_position_data['position'] = last_count.position

        kwargs['last_position'] = last_position_data
        kwargs['inventory'] = inventory_instance
        kwargs['product_status'] = ProductStatus.objects.all()
        kwargs['storage_types'] = StorageType.objects.all()

        return super().get_context_data(**kwargs)


class InventoryCountImageView(LoginRequiredMixin, View):
    template_name = 'inventory_control/image_error.html'

    def get(self, request, *args, **kwargs):
        inventory_count = InventoryCount.objects.filter(pk=kwargs['pk']).first()
        if not inventory_count:
            return render(
                request,
                self.template_name,
                {
                    'message': 'Imagen no encontrada o enlace invalido.',
                    'inventory_count': None,
                },
                status=404,
            )

        if not inventory_count.image:
            return render(
                request,
                self.template_name,
                {
                    'message': 'Este registro no tiene una imagen asociada.',
                    'inventory_count': inventory_count,
                },
                status=404,
            )

        try:
            with inventory_count.image.open('rb') as image_file:
                image_file.seek(0)
                with Image.open(image_file) as img:
                    img.verify()

            inventory_count.image.open('rb')
            content_type = mimetypes.guess_type(inventory_count.image.name)[0] or 'application/octet-stream'
            return FileResponse(inventory_count.image.file, content_type=content_type)
        except (FileNotFoundError, OSError, ValueError, UnidentifiedImageError, SuspiciousFileOperation):
            return render(
                request,
                self.template_name,
                {
                    'message': 'Imagen danada o corrupta, no puede abrirse o servidor no puedo mostrarla',
                    'inventory_count': inventory_count,
                },
                status=422,
            )
