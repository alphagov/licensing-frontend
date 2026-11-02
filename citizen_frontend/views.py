from common.models.authority import Authority
from django.http import FileResponse
from django.shortcuts import render

import citizen_frontend.services.licence_lookup_service as licence_lookup_service


def display_licence_unavailable_online(request, authority: Authority):
    return render(
        request,
        "citizen_frontend/licence_not_available_online_page.html",
        {
            "title": "This licence is currently not available online",
            "contact_information": authority.contact_details,
            "authority_name": authority.full_name,
        },
    )


def display_licence_must_be_applied_for_locally(request, authority_url=None):
    return render(
        request,
        "citizen_frontend/licence_must_be_applied_for_locally_page.html",
        {"title": "This licence must be applied for locally", "authority_url": authority_url},
    )


def generate_form(
    request, authority_slug: str, licence_slug: str, licence_code: str, interaction_id: int, interaction_sub_id: int
):

    # TODO we want to get form details, and only if they exist should we get the customisation.
    #   feels like this could be wrapped in a service.
    #   e.g PDFFormProvider that is made up of licencelookup and PDF generation.
    #   licencelooup is already made up of auth_repo, licence_repo, and customisation_repo
    #   perhaps refactor to class based, can leverage composition, DI, etc more module code.

    licence_lookup_service.lookup_form_details(
        authority_slug=authority_slug,
        licence_slug=licence_slug,
        interaction_id=interaction_id,
        interaction_sub_id=interaction_sub_id,
    )

    with open("citizen_frontend/tests/resources/test_forms/temporary-event-notice.pdf", "rb") as f:
        return FileResponse(f.read(), content_type="application/pdf")
