from common.models.authorities import LicenceDetails
from common.models.interaction_customisations import Customisation
from common.models.licences import LicenceInteraction
from django.http import Http404
from django.shortcuts import render

import citizen_frontend.api.repository.interaction_customisation_repository as interaction_customisation_repository
from citizen_frontend.api.utils import INTERACTION_WORD_MAPPING
from citizen_frontend.forms.licence_submission import ApplicationSubmissionForm
from citizen_frontend.mocks import get_mocked_context
from citizen_frontend.services import licence_lookup_service


def _get_published_customisation_or_redirect(
    authority_slug: str, licence_code: str, interaction: LicenceInteraction
) -> Customisation:
    published_customisation = interaction_customisation_repository.find_published_customisation(
        authority_slug,
        licence_code,
        interaction.interaction_id,
        interaction.interaction_sub_id,
    )
    if not published_customisation:
        raise Http404("suspended") from None
    return published_customisation


def _get_correct_url_for_legislation(licence_details: LicenceDetails, published_customisation: Customisation):
    return published_customisation.information_url or licence_details.authority_url


def begin_application_steps(
    request, licence_slug: str, authority_slug: str, interaction_id: str, interaction_sub_id: int
):
    try:
        interaction_type = INTERACTION_WORD_MAPPING.get(interaction_id)
        if interaction_type is None:
            raise Http404("bad interaction") from None
        try:
            licence, authority, interaction, licence_details = licence_lookup_service.get_licence_interaction_context(
                authority_slug, licence_slug, interaction_type, interaction_sub_id
            )
        except RuntimeError:
            raise Http404("missing context") from None

        if not licence_details.can_apply_via_licensify:
            raise Http404("unhandled") from None

        published_customisation = _get_published_customisation_or_redirect(
            authority_slug, licence.licence_code, interaction
        )
        fixed_fee_amount = 0
        if published_customisation.is_fee_required and published_customisation.fixed_fee_amount:
            fixed_fee_amount = published_customisation.fixed_fee_amount
        licence_name = (
            interaction.licence_interaction_name if len(interaction.display_title) < 1 else interaction.display_title
        )
        legislation_info_url = _get_correct_url_for_legislation(licence_details, published_customisation)
        general_info_url = published_customisation.guidance_url
        before_you_apply_required = (
            published_customisation.is_fee_required or published_customisation.supporting_document_definitions
        )
        context = {
            "authority_name": authority.full_name.title(),
            "licence_name": licence_name,
            "interaction_sub_id": interaction_sub_id,
            "interaction_id": interaction_id,
            "is_fee_required": published_customisation.is_fee_required,
            "fee_amount": None
            if fixed_fee_amount == 0
            else published_customisation.fixed_fee_amount.format_to_string_in_pounds,
            "steps": 4 if published_customisation.is_fee_required else 3,
            "authority_slug": authority.url_slug,
            "licence_slug": licence.url_slug,
            "supporting_documents": published_customisation.supporting_document_definitions,
            "general_info_url": published_customisation.guidance_url,
            "legislation_info_url": legislation_info_url,
            "is_postal_allowed": published_customisation.is_postal_allowed,
            "additional_info_exists": legislation_info_url or general_info_url,
            "before_you_apply_required": before_you_apply_required,
        }
        context.update({"step": 1})
        return render(request, "citizen_frontend/licence_introduction_page.html", context)
    except Http404:
        raise
    except Exception as e:
        raise Http404("Incorrect licence, or authority does not exist") from e


def submit_form(request, licence_slug: str, authority_slug: str, interaction_id: str, interaction_sub_id: int):
    try:
        context = get_mocked_context(licence_slug, authority_slug, interaction_id, interaction_sub_id)
        context.update({"step": 2})

        if request.method == "POST":
            form = ApplicationSubmissionForm(
                request.POST,
                fee=context.get("fee_amount"),
                supporting_documents=context.get("supporting_documents"),
                default_declarations=context.get("default_declarations"),
            )

            if form.is_valid():
                pass

        else:
            form = ApplicationSubmissionForm(
                fee=context.get("fee_amount"),
                supporting_documents=context.get("supporting_documents"),
                default_declarations=context.get("default_declarations"),
            )

        context.update({"form": form})

        return render(request, "citizen_frontend/licence_submission_page.html", context)

    except Exception as e:
        raise Http404("Incorrect licence, or authority does not exist") from e
