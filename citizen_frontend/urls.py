from django.urls import path

from . import views

urlpatterns = [
    path("<str:licence>/<str:authority>/<str:interaction>-<int:interation_sub_id>", views.index, name="index"),
    path(
        "<str:licence>/<str:authority>/<str:interaction>-<int:interation_sub_id>/form", views.submit_form, name="submit"
    ),
    path("api/licences", views.get_all_licences, name="get_all_licences"),
]
