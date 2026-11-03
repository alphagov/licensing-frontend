from common.models.authority import Authority
from django.http import FileResponse, HttpResponse
from django.shortcuts import render

from citizen_frontend.services.pdf_provider import PdfGenerator


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
    #   e.g PDFFormProvider ABC that has a generate and flatten method on it
    #   Concrete implementation is APTOFormProvider that is made up of licencelookup, department lookup etc.
    #   licencelooup is already made up of auth_repo, licence_repo, and customisation_repo
    #   perhaps refactor to class based, can leverage composition, DI, etc more modular code.

    # licence, authority, interaction, _ = licence_lookup_service.get_licence_interaction_context(
    #     authority_url_slug=authority_slug,
    #     licence_url_slug=licence_slug,
    #     interaction=interaction_id,
    #     interaction_sub_id=interaction_sub_id,
    # )
    #
    # published_customisation = licence_lookup_service.interaction_customisation_repository.
    # find_published_customisation(
    #     authority_url_slug=authority_slug,
    #     licence_code=licence_code,
    #     interaction_sub_id=interaction_sub_id,
    #     interaction_id=interaction_id,
    # )
    # department_repo = DepartmentRepo()
    # department = department_repo.get_by_id(department_id=published_customisation.department)

    # pdf_provider = APTOPdfProvider()
    # pdf_provider.generate_pdf(
    #     authority=authority,
    #     licence=licence,
    #     customisation=published_customisation,
    #     department=department,
    #     return_url=""
    # )

    pdf_generator = PdfGenerator()

    file, file_name = pdf_generator.handle_request(
        authority_slug=authority_slug,
        licence_slug=licence_slug,
        licence_code=licence_code,
        interaction_id=interaction_id,
        interaction_sub_id=interaction_sub_id,
    )

    return FileResponse(file, content_type="application/pdf", filename=file_name, as_attachment=True)
    return HttpResponse("hello world")
