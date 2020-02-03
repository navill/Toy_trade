from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView


class GoogleMapView(ListView):
    template_name = 'location/test_google_map.html'
