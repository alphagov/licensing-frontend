import logging

from django.http import Http404
from django.shortcuts import render

from citizen_frontend.api.utils import INTERACTION_WORD_MAPPING
from citizen_frontend.forms.licence_submission import ApplicationSubmissionForm
from citizen_frontend.repository import interaction_customisation_repository
from citizen_frontend.services import licence_lookup_service
from citizen_frontend.services.application_upload_service import ApplicationUploadService
from citizen_frontend.views import display_licence_must_be_applied_for_locally, display_licence_unavailable_online

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def generate_application_form(
    request, licence_slug: str, authority_slug: str, interaction_id: str, interaction_sub_id: int
):
    try:
        interaction_type = INTERACTION_WORD_MAPPING.get(interaction_id)
        if interaction_type is None:
            raise Http404("Invalid interaction ID") from None

        licence, authority, interaction, licence_details = licence_lookup_service.get_licence_interaction_context(
            authority_slug, licence_slug, interaction_type, interaction_sub_id
        )

        if not licence_details.can_apply_via_licensify:
            return display_licence_must_be_applied_for_locally(request, licence_details.authority_url)

        published_customisation = interaction_customisation_repository.find_published_customisation(
            authority_slug, licence.licence_code, interaction.interaction_id, interaction.interaction_sub_id
        )

        if not published_customisation:
            return display_licence_unavailable_online(request, authority)

        licence_name = (
            interaction.licence_interaction_name if len(interaction.display_title) < 1 else interaction.display_title
        )

        context = {
            "authority": authority,
            "licence_name": licence_name,
            "interaction_sub_id": interaction_sub_id,
            "interaction": interaction_id,
            "published_customisation": published_customisation,
        }

        context.update({"step": 2})

        if request.method == "POST":
            form = ApplicationSubmissionForm(
                request.POST,
                request.FILES,
                published_customisation=context.get("published_customisation"),
            )

            if form.is_valid():
                upload_service = ApplicationUploadService()
                upload_service.upload_application(request.FILES["application_upload"])

        else:
            form = ApplicationSubmissionForm(
                published_customisation=context.get("published_customisation"),
            )

        context.update({"form": form})

        return render(request, "citizen_frontend/licence_submission_page.html", context)

    except Exception as e:
        logger.error(e)
        raise Http404("Incorrect licence, or authority does not exist") from e
