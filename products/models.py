from django.db import models
from django.urls import reverse
    

class Brand(models.Model):
    name = models.CharField(max_length=150)
    country = models.ForeignKey('geo.Country', on_delete=models.PROTECT, related_name='brands', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.name


class Product(models.Model):

    created = models.DateTimeField(auto_now_add=True)
    sku = models.CharField(max_length=100)
    description = models.TextField()
    active = models.BooleanField(default=True)
    brand = models.ForeignKey(
        Brand, 
        on_delete=models.CASCADE, 
        related_name='products',
        null=True,
        blank=True
    )
    country = models.ForeignKey('geo.Country', on_delete=models.PROTECT, related_name='products', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Productos'

    def get_absolute_url(self):
        return reverse('products:product_update', args=[self.pk])

    def __str__(self) -> str:
        return self.description


