from django import forms
from .models import City
from .utilities import temp_queryset


class CityForm(forms.ModelForm):
    # temp = forms.ModelChoiceField(queryset=temp_queryset, label='Температура', empty_label='Цельсий')

    class Meta:
        model = City
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'name': 'city_name',
                                            'placeholder': 'Введите название города'
                                            })}
