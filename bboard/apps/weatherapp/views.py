from django.shortcuts import render
import requests


def index(request):
    appid = '57725f55f04ae1d78715ff2234f8dfa6'
    url = 'https://api.openweathermap.org/data/2.5/' \
          'weather?q={}&units={}&appid={}'
    temp = 'metric'
    city = 'London'
    res = requests.get(url.format(city, temp, appid)).json()

    city_info = {
        'city': city,
        'temp': res['main']['temp'],

    } #'icon': res['weather']['icon']

    context = {
        'info': city_info
    }

    return render(request, 'weather/index.html', city_info)

