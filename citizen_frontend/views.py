from common.models.authority import Authority
from django.http import FileResponse
from django.shortcuts import render

from citizen_frontend.exceptions import PDFGenerationGeneralError, PDFProviderUnavailableError
from citizen_frontend.services.pdf_generation.pdf_generator import PdfGenerator


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
    try:
        pdf_generator = PdfGenerator()

        file, file_name = pdf_generator.handle_request(
            authority_slug=authority_slug,
            licence_slug=licence_slug,
            licence_code=licence_code,
            interaction_id=interaction_id,
            interaction_sub_id=interaction_sub_id,
        )

        return FileResponse(file, content_type="application/pdf", filename=file_name, as_attachment=True)
    except PDFGenerationGeneralError:
        return render(
            request=request,
            template_name="citizen_frontend/error.html",
            context={"title": "An error has occurred"},
            status=500,
        )
    except PDFProviderUnavailableError:
        return render(
            request=request,
            template_name="citizen_frontend/error.html",
            context={"title": "An error has occurred", "message": "The PDF form is unavailable at the moment."},
            status=503,
        )

    # TODO current template passes an exception ID in
