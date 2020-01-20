from django.urls import path, include
from .views import index

app_name = 'weather'
urlpatterns = [
    path('', index, name='index'),
]