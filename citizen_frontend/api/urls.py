from django.urls import path

from . import find_a_licence_integration

urlpatterns = [
    path("licences", find_a_licence_integration.get_all_licences, name="get_all_licences"),
]
