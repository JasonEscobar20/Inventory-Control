from django.db import models
from django.contrib.auth import get_user_model


class Country(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ('name',)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile')
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='users', null=True, blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
