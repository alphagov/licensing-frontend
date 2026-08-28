from django.urls import path

from . import find_a_licence_integration

urlpatterns = [
    path("licences", find_a_licence_integration.get_all_licences, name="get_all_licences"),
    path(
        "licences/<str:licence_code>",
        find_a_licence_integration.get_licence_authority_and_interactions_by_licence_code,
        name="get_licence_authority_and_interactions_by_licence_code",
    ),
    path(
        "licences/<str:licence_code>/<str:snac_code>",
        find_a_licence_integration.get_licence_authorities_and_interactions_by_licence_code_and_snac_code,
        name="get_licence_authorities_and_interactions_by_licence_code_and_snac_code",
    ),
]
