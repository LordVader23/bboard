from django.shortcuts import render
from .models import City
from .forms import CityForm
import requests


def index(request):
    appid = '57725f55f04ae1d78715ff2234f8dfa6'
    url = 'https://api.openweathermap.org/data/2.5/' \
          'weather?q={}&units={}&appid={}&lang={}'
    temp = 'metric'
    city1 = 'London'
    lang = 'en'

    if request.method == 'POST':
        form = CityForm(request.POST)
        form.save()

    form = CityForm()

    cities = City.objects.all()
    all_cities = []

    for city2 in cities:
        res = requests.get(url.format(city2.name, temp, appid, lang)).json()
        city_info = {
            'city': city2.name,
            'temp': res['main']['temp'],
            'icon': res['weather'][0]['icon']

        }

        all_cities.append(city_info)

    context = {
        'cities': all_cities,
        'form': form
    }

    return render(request, 'weather/index.html', context)

