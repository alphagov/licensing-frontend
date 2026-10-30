from typing import Any

from common.models.authority import Authority, LicenceDetail
from common.models.interaction_customisation import Customisation
from common.models.licence import Licence, LicenceInteraction
from django.http import Http404
from django.shortcuts import render

from citizen_frontend.api.utils import INTERACTION_WORD_MAPPING
from citizen_frontend.repository import interaction_customisation_repository
from citizen_frontend.services import licence_lookup_service
from citizen_frontend.views import display_licence_must_be_applied_for_locally, display_licence_unavailable_online


def begin_application_steps(
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

        context = build_context(
            authority,
            interaction,
            interaction_id,
            licence,
            licence_details,
            published_customisation,
        )

        return render(request, "citizen_frontend/licence_introduction_page.html", context)
    except Http404:
        raise
    except Exception as e:
        raise Http404("Incorrect licence, or authority does not exist") from e


def build_context(
    authority: Authority,
    interaction: LicenceInteraction,
    interaction_id: str,
    licence: Licence,
    licence_details: LicenceDetail,
    published_customisation: Customisation,
) -> dict[str | Any, int | str | None | Any]:

    fee_amount = (
        published_customisation.fixed_fee_amount.format_to_string_in_pounds
        if published_customisation.is_fee_required and published_customisation.fixed_fee_amount
        else None
    )

    licence_name = (
        interaction.licence_interaction_name if len(interaction.display_title) < 1 else interaction.display_title
    )
    legislation_info_url = _get_correct_url_for_legislation(licence_details, published_customisation)
    general_info_url = published_customisation.guidance_url

    context = {
        "licence": licence,
        "authority": authority,
        "licence_name": licence_name,
        "interaction": interaction,
        "interaction_id": interaction_id,
        "is_fee_required": published_customisation.is_fee_required,
        "fee_amount": fee_amount,
        "steps": 4 if published_customisation.is_fee_required else 3,
        "supporting_documents": published_customisation.supporting_document_definitions,
        "general_info_url": published_customisation.guidance_url,
        "legislation_info_url": legislation_info_url,
        "is_postal_allowed": published_customisation.is_postal_allowed,
        "additional_info_exists": legislation_info_url or general_info_url,
        "before_you_apply_required": published_customisation.is_fee_required
        or published_customisation.supporting_document_definitions,
    }
    context.update({"step": 1})

    return context


def _get_correct_url_for_legislation(licence_details: LicenceDetail, published_customisation: Customisation):
    return published_customisation.information_url or licence_details.authority_url
