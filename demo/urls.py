from django.urls import path

from . import views


urlpatterns = [
    path('api/flight-search', views.flight, name='flight-search'),
    path('', views.demo, name='book-flight'),
    path('origin_airport_search/', views.origin_airport_search,
         name='origin_airport_search'),
    path('destination_airport_search/', views.destination_airport_search,
         name='destination_airport_search'),
]
