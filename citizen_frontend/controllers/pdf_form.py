import logging

from django.http import FileResponse, Http404
from django.shortcuts import render

import citizen_frontend.services.licence_lookup_service as licence_lookup_service
from citizen_frontend.exceptions import (
    FormNotFoundException,
    FormNotPublishedException,
    LicenceLookupError,
    PDFGenerationGeneralError,
    PDFProviderUnavailableError,
)
from citizen_frontend.services.pdf_generation.pdf_generator import PdfGenerator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def generate_pdf_form(
    request, authority_slug: str, licence_slug: str, licence_code: str, interaction_id: int, interaction_sub_id: int
):
    try:
        licence, authority, interaction, _ = licence_lookup_service.get_licence_interaction_context(
            authority_url_slug=authority_slug,
            licence_url_slug=licence_slug,
            interaction=interaction_id,
            interaction_sub_id=interaction_sub_id,
        )

        published_customisation = (
            licence_lookup_service.interaction_customisation_repository.find_published_customisation(
                authority_url_slug=authority_slug,
                licence_code=licence_code,
                interaction_id=interaction_id,
                interaction_sub_id=interaction_sub_id,
            )
        )
        if not published_customisation:
            #  instead of raise exception, do the render here
            # TODO creat page to render authority contact details
            raise FormNotPublishedException(f"No form published for {authority.name}")

        pdf_generator = PdfGenerator()

        file, file_name = pdf_generator.handle_request(
            authority=authority,
            licence=licence,
            interaction=interaction,
            customisation=published_customisation,
        )

        return FileResponse(file, content_type="application/pdf", filename=file_name, as_attachment=True)
    except PDFGenerationGeneralError as e:
        logger.error("%s: %s", e.id, e.args)
        return render(
            request=request,
            template_name="citizen_frontend/error.html",
            context={"title": "An error has occurred", "error_id": e.id},
            status=500,
        )
    except PDFProviderUnavailableError as e:
        logger.error("%s: %s", e.id, e.args)
        return render(
            request=request,
            template_name="citizen_frontend/error.html",
            context={
                "title": "An error has occurred",
                "message": "The PDF form is unavailable at the moment.",
                "error_id": e.id,
            },
            status=503,
        )
    except FormNotFoundException as e:
        logger.error(e.args)
        raise Http404 from e
    except LicenceLookupError as e:
        logger.error(e.args)
        logger.error(
            "No form found for %s, %s, %s, %s, %s",
            authority_slug,
            licence_slug,
            licence_code,
            interaction_id,
            interaction_sub_id,
        )
        raise Http404 from e
