from common.models.authority import Authority
from django.shortcuts import render


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


def generate_form():
    return None
