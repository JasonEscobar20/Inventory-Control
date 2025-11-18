from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

    def __str__(self):
        return self.name


class Employee(models.Model):
    code = models.CharField(max_length=50)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    
    active = models.BooleanField(default=True)
    country = models.ForeignKey('geo.Country', on_delete=models.PROTECT, related_name='employees', null=True, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='employees',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ('last_name',)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'