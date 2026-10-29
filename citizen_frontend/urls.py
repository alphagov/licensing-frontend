from django.urls import path

from . import views

urlpatterns = [
    path(
        "<str:licence_slug>/<str:authority_slug>/<str:interaction_id>-<int:interaction_sub_id>",
        views.begin_application_steps,
        name="begin_application_steps",
    ),
    path(
        "<str:licence_slug>/<str:authority_slug>/<str:interaction_id>-<int:interaction_sub_id>/form",
        views.submit_form,
        name="submit",
    ),
    path(
        "forms/<str:authority_slug>/<str:licence_slug>/<str:licence_code>,<int:interaction_id>-<int:interaction_sub_id>",
        views.generate_form,
        name="generate_form",
    ),
]
