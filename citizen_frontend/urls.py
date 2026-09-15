from django.urls import path

from . import views

urlpatterns = [
    path(
        "<str:licence_slug>/<str:authority_slug>/<str:interaction_id>-<int:interation_sub_id>",
        views.index,
        name="index",
    ),
    path(
        "<str:licence_slug>/<str:authority_slug>/<str:interaction_id>-<int:interation_sub_id>/form",
        views.submit_form,
        name="submit",
    ),
]
