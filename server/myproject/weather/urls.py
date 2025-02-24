from django.urls import path
from . import views

urlpatterns = [
    path('<str:city>/', views.get_weather, name='get_weather'),
]
