from django.db import models


class City(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название города')

    def __str__(self):
        return self.name
