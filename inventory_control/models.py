from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from products.models import Product
from employees.models import Employee

class Warehouse(models.Model):
    name = models.CharField(max_length=150)

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
        (3, 'Eliminado')
    )

    created = models.DateTimeField(auto_now_add=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='inventories')
    employee = models.ForeignKey(Employee, on_delete=models.PROTECT, related_name='inventories')
    store = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='inventories')
    description = models.TextField()
    status = models.PositiveIntegerField(choices=STATUS, default=1)

    class Meta:
        verbose_name_plural = 'Inventarios'

    def get_absolute_url(self):
        return reverse('inventory_control:inventory-control-update', args=[self.pk])


class MeasurementUnit(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'Unidad de medida'
        verbose_name_plural = 'Unidades de medida'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Side(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'Lado'
        verbose_name_plural = 'Lado'
        ordering = ('name',)

    def __str__(self):
        return self.name


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
    measurement_unit = models.ForeignKey(MeasurementUnit, on_delete=models.PROTECT, related_name='inventory_records')
    product_status = models.ForeignKey(ProductStatus, on_delete=models.PROTECT, related_name='inventory_records')
    side = models.ForeignKey(Side, on_delete=models.PROTECT, related_name='inventory_records')
    storage_type = models.ForeignKey(StorageType, on_delete=models.PROTECT, related_name='inventory_records')
    entry_date = models.DateField(blank=True)
    storage_position = models.PositiveIntegerField(default=1)
    level = models.PositiveIntegerField(default=1)
    position = models.PositiveIntegerField(default=1)
    amount = models.PositiveIntegerField(default=1)
    expiration_date = models.DateField(blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Conteos de inventario'





