from django.urls import path
from .views import FuelStopAPI

urlpatterns = [
    path('fuel_stops/', FuelStopAPI.as_view(), name='fuel_stops'),
]
