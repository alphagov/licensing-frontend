from django.urls import path

from . import views
from .api import find_a_licence_integration

urlpatterns = [
    path("<str:licence>/<str:authority>/<str:interaction>-<int:interation_sub_id>", views.index, name="index"),
    path(
        "<str:licence>/<str:authority>/<str:interaction>-<int:interation_sub_id>/form", views.submit_form, name="submit"
    ),
    path("api/licences/", find_a_licence_integration.get_all_licences, name="get_all_licences"),
]
