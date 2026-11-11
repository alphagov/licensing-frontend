import logging

from django.http import FileResponse
from django.shortcuts import render

from citizen_frontend.exceptions import PDFGenerationGeneralError, PDFProviderUnavailableError
from citizen_frontend.services.pdf_generation.pdf_generator import PdfGenerator

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def generate_pdf_form(
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
    except PDFGenerationGeneralError as e:
        logger.error("%s: $S", e.id, e.args)
        return render(
            request=request,
            template_name="citizen_frontend/error.html",
            context={"title": "An error has occurred"},
            status=500,
        )
    except PDFProviderUnavailableError as e:
        logger.error("%s: $S", e.id, e.args)
        return render(
            request=request,
            template_name="citizen_frontend/error.html",
            context={"title": "An error has occurred", "message": "The PDF form is unavailable at the moment."},
            status=503,
        )

    # TODO current template passes an exception ID in
