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
        "payment/licenceCallback",
        views.payment_licence_callback,
        name="payment_licence_callback",
    ),
]
