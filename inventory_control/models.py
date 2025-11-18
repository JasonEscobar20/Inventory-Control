from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from products.models import Product
from employees.models import Employee

class Warehouse(models.Model):
    name = models.CharField(max_length=150)
    country = models.ForeignKey('geo.Country', on_delete=models.PROTECT, related_name='warehouses', null=True, blank=True)

    class Meta:
        verbose_name = 'Bodega'
        verbose_name_plural = 'Bodegas'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Inventory(models.Model):
    STATUS = (
        (1, 'Iniciado'),
        (2, 'Finalizado'),
        (3, 'Confirmado'),
    )

    created = models.DateTimeField(auto_now_add=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='inventories')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='inventories')
    store = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='inventories')
    status = models.PositiveIntegerField(choices=STATUS, default=1)
    inventory_date = models.DateField(blank=True, null=True)
    # country se deriva del warehouse / employee, opcional directo
    country = models.ForeignKey('geo.Country', on_delete=models.PROTECT, related_name='inventories', null=True, blank=True)
    # audit timestamps/users for status transitions
    finished_at = models.DateTimeField(blank=True, null=True)
    finished_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='inventories_finished')
    confirmed_at = models.DateTimeField(blank=True, null=True)
    confirmed_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, null=True, blank=True, related_name='inventories_confirmed')

    class Meta:
        verbose_name_plural = 'Inventarios'

    def get_absolute_url(self):
        return reverse('inventory_control:inventory-control-update', args=[self.pk])

    def can_transition_to(self, new_status: int) -> bool:
        """Return True if transition from current status to new_status is allowed."""
        current = self.status
        # Allowed sequence: 1 -> 2 -> 3. No backwards or skipping 1->3 directly.
        if new_status == current:
            return True
        if current == 1 and new_status == 2:
            return True
        if current == 2 and new_status == 3:
            return True
        return False

    def apply_transition(self, new_status: int, user=None):
        if not self.can_transition_to(new_status):
            raise ValueError('Transición de estado no permitida.')
        if new_status == self.status:
            return
        if new_status == 2:  # Finalizado
            self.finished_at = timezone.now()
            if user:
                self.finished_by = user
        if new_status == 3:  # Confirmado
            # ensure finished before confirm
            if self.status != 2 and not self.finished_at:
                raise ValueError('No se puede confirmar un inventario sin estar finalizado.')
            self.confirmed_at = timezone.now()
            if user:
                self.confirmed_by = user
        self.status = new_status


class StorageType(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'Tipo de almacenamiento'
        verbose_name_plural = 'Tipos de almacenamiento'
        ordering = ('name',)

    def __str__(self):
        return self.name


class ProductStatus(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'Estado del producto'
        verbose_name_plural = 'Estado del producto'
        ordering = ('name',)

    def __str__(self):
        return self.name


class InventoryCount(models.Model):
    

    created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='inventory_records')

    inventory = models.ForeignKey(Inventory, on_delete=models.PROTECT, related_name='inventory_records')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='inventory_records')
    product_status = models.ForeignKey(ProductStatus, on_delete=models.PROTECT, related_name='inventory_records')
    storage_type = models.ForeignKey(StorageType, on_delete=models.PROTECT, related_name='inventory_records')
    position_letter = models.CharField(max_length=1, default='A')
    level = models.PositiveIntegerField(default=1)
    position = models.PositiveIntegerField(default=1)
    amount = models.PositiveIntegerField(default=1)
    active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='inventory_counts/', null=True, blank=True)
    country = models.ForeignKey('geo.Country', on_delete=models.PROTECT, related_name='inventory_counts', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Conteos de inventario'





