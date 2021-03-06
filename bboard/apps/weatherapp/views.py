from django.shortcuts import render
from .models import City
from .forms import CityForm
import requests


def index(request):
    # Default values
    appid = '57725f55f04ae1d78715ff2234f8dfa6'
    url = 'https://api.openweathermap.org/data/2.5/' \
          'weather?q={}&units={}&appid={}&lang={}'
    temp = 'metric'
    city1 = 'London'
    lang = 'en'

    if request.method == 'POST':
        form = CityForm(request.POST)

        if form.is_valid():
            form.save()

        # Clear form
        form = CityForm()

        if 'temp_select' in request.POST:
            temp_code = request.POST['temp_select']

            if temp_code == '0':
                temp = 'kelvin'
            elif temp_code == '1':
                temp = 'metric'
            elif temp_code == '2':
                temp = 'imperial'

        if 'lang_select' in request.POST:
            lang_code = request.POST['lang_select']

            if lang_code == '0':
                lang = 'en'
            elif lang_code == '1':
                lang = 'ru'

        # Main_city - city, which was added to the form field
        city1 = request.POST['name']
        res = requests.get(url.format(city1, temp, appid, lang)).json()
        info = {
            'city': res['name'],
            'temp': res['main']['temp'],
            'icon': res['weather'][0]['icon']
        }

        # Get cities from model City and prepare they for adding to context
        cities = City.objects.all()
        all_cities = []

        for city2 in cities:
            res = requests.get(url.format(city2.name, temp, appid, lang)).json()
            city_info = {
                'city': res['name'],
                'temp': res['main']['temp'],
                'icon': res['weather'][0]['icon']

            }
            # list for context
            all_cities.append(city_info)

        context = {
            'main_city': info,
            'cities': all_cities,
            'form': form,
            'temp': temp
        }
    else:
        form = CityForm()

        # Get cities from model City and prepare they for adding to context
        cities = City.objects.all()
        all_cities = []

        for city2 in cities:
            res = requests.get(url.format(city2.name, temp, appid, lang)).json()
            city_info = {
                'city': res['name'],
                'temp': res['main']['temp'],
                'icon': res['weather'][0]['icon']

            }
            # list for context
            all_cities.append(city_info)

        context = {
            'main_city': False,
            'cities': all_cities,
            'form': form,
            'temp': temp
        }

    return render(request, 'weather/index.html', context)

