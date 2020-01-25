from django import forms
from .models import City


class CityForm(forms.ModelForm):
    class Meta:
        model = City
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'name': 'city_name',
                                            'placeholder': 'Введите название города'
                                            })}
