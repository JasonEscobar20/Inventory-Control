from django.db import models


class Employee(models.Model):
    code = models.CharField(max_length=50)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ('last_name',)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'