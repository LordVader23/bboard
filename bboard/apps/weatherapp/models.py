from django.db import models


class City(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название города', unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Города'
        verbose_name = 'Город'
