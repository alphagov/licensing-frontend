from common.models.interaction_customisations import Customisation
from django.http import Http404
from django.shortcuts import render

import citizen_frontend.api.repository.interaction_customisation_repository as interaction_customisation_repository
from citizen_frontend.api.utils import INTERACTION_WORD_MAPPING
from citizen_frontend.forms.licence_submission import ApplicationSubmissionForm
from citizen_frontend.mocks import get_mocked_context
from citizen_frontend.services import licence_lookup_service
from citizen_frontend.services.licence_lookup_service import LicenceInteractionContext


def _redirect_if_no_context(context: LicenceInteractionContext):
    if context is None:
        raise Http404("missing details") from None


def _redirect_if_cant_apply_via_licensify(context: LicenceInteractionContext):
    if not context.licence_detail.can_apply_via_licensify:
        raise Http404("unhandled") from None


def _get_published_customisation_or_redirect(context: LicenceInteractionContext, authority_slug: str) -> Customisation:
    published_customisation = interaction_customisation_repository.find_published_customisation(
        authority_slug,
        context.licence.licence_code,
        context.interaction.interaction_id,
        context.interaction.interaction_sub_id,
    )
    if not published_customisation:
        raise Http404("suspended") from None
    return published_customisation


def _get_correct_url_for_legislation(
    full_licence_interaction_context: LicenceInteractionContext, published_customisation: Customisation
):
    return published_customisation.information_url or full_licence_interaction_context.licence_detail.authority_url


def begin_application_steps(
    request, licence_slug: str, authority_slug: str, interaction_id: str, interaction_sub_id: int
):
    try:
        interaction = INTERACTION_WORD_MAPPING.get(interaction_id)
        if interaction is None:
            raise Http404("bad interaction") from None
        full_licence_interaction_context = licence_lookup_service.get_licence_interaction_context(
            authority_slug, licence_slug, interaction_id, interaction_sub_id
        )

        _redirect_if_no_context(full_licence_interaction_context)
        _redirect_if_cant_apply_via_licensify(full_licence_interaction_context)
        published_customisation = _get_published_customisation_or_redirect(
            full_licence_interaction_context, authority_slug
        )
        fixed_fee_amount = 0
        if published_customisation.is_fee_required and published_customisation.fixed_fee_amount:
            fixed_fee_amount = published_customisation.fixed_fee_amount
        licence_name = (
            full_licence_interaction_context.interaction.licence_interaction_name
            if len(full_licence_interaction_context.interaction.display_title) < 1
            else full_licence_interaction_context.interaction.display_title
        )
        legislation_info_url = _get_correct_url_for_legislation(
            full_licence_interaction_context, published_customisation
        )
        general_info_url = published_customisation.guidance_url
        before_you_apply_required = (
            published_customisation.is_fee_required or published_customisation.supporting_document_definitions
        )
        context = {
            "authority_name": full_licence_interaction_context.authority.full_name.title(),
            "licence_name": licence_name,
            "interaction_sub_id": interaction_sub_id,
            "interaction_id": interaction_id,
            "is_fee_required": published_customisation.is_fee_required,
            "fee_amount": None
            if fixed_fee_amount == 0
            else published_customisation.fixed_fee_amount.format_to_string_in_pounds,
            "steps": 4 if published_customisation.is_fee_required else 3,
            "authority_slug": full_licence_interaction_context.authority.url_slug,
            "licence_slug": full_licence_interaction_context.licence.url_slug,
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
