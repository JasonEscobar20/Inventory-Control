from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
        verbose_name_plural = 'Categorias'

    def __str__(self):
        return self.name


class Type(models.Model):
    name = models.CharField(max_length=150)

    class Meta:
        verbose_name_plural = 'Tipo de producto'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    type = models.ForeignKey(Type, on_delete=models.PROTECT, related_name='products')

    created = models.DateTimeField(auto_now_add=True)
    sku = models.CharField(max_length=100)
    description = models.TextField()
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Productos'
        ordering = ('category__name',)

    def get_absolute_url(self):
        return reverse('products:product_update', args=[self.pk])

    def __str__(self) -> str:
        return self.description


