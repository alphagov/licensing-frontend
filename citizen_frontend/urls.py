from django.urls import path

from citizen_frontend.controllers.application_form import generate_application_form
from citizen_frontend.controllers.begin_application import begin_application_steps

from . import views

urlpatterns = [
    path(
        "<str:licence_slug>/<str:authority_slug>/<str:interaction_id>-<int:interaction_sub_id>",
        begin_application_steps,
        name="begin_application_steps",
    ),
    path(
        "<str:licence_slug>/<str:authority_slug>/<str:interaction_id>-<int:interaction_sub_id>/form",
        generate_application_form,
        name="submit",
    ),
    path(
        "forms/<str:authority_slug>/<str:licence_slug>/<str:licence_code>,<int:interaction_id>-<int:interaction_sub_id>",
        views.generate_form,
        name="generate_form",
    ),
]
