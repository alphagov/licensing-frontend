from django.urls import path

from . import views

urlpatterns = [
    path("<str:licence>/<str:authority>/<str:interaction>-<int:interation_sub_id>", views.index, name="index"),
]
