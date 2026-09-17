from django.http import Http404
from django.shortcuts import render

import citizen_frontend.api.repository.interaction_customisation_repository as interaction_customisation_repository
from citizen_frontend.forms.licence_submission import ApplicationSubmissionForm
from citizen_frontend.services import licence_lookup_service


# i started doing the wrong thing, rather than delete it i'm going to leave it here for now but this is actually the start page where you select an interaction
# def start(request):
#     authority = authority_repository.get_authority_by_url_slug(authority_slug)
#     licence = licence_repository.get_licence_by_url_slug(licence_slug)
#
#     matching_authority_licence = [
#         details for details in authority.licence_details if details.licence_code == licence.licence_code
#     ]
#     if len(matching_authority_licence) > 1:
#         # TODO error handle better
#         raise RuntimeError(f"Bad data, duplicate entries for licence code '{licence.licence_code}'")
#     if not (len(matching_authority_licence) == 1 and matching_authority_licence[0].using_gov_uk):
#         # TODO return not found
#         pass
def index(request, licence_slug: str, authority_slug: str, interaction_id: str, interation_sub_id: int):
    try:
        full_licence_interaction_context = licence_lookup_service.get_licence_interaction_context(
            authority_slug, licence_slug, interaction_id, interation_sub_id
        )
        if not full_licence_interaction_context:
            raise Http404("Incorrect licence, or authority does not exist") from None
        # TODO if handled by gov
        # if full_licence_interaction_context.licence_detail.handled_by_gov
        published_customisation = interaction_customisation_repository.find_published_customisation(
            authority_slug,
            full_licence_interaction_context.licence.licence_code,
            full_licence_interaction_context.interaction.interaction_id,
            full_licence_interaction_context.interaction.interaction_sub_id,
        )
        if not published_customisation:
            # TODO this actually checks to see if a licence has been suspended or something
            raise Http404("Incorrect licence, or authority does not exist") from None
        fixed_fee_amount = 0
        if published_customisation.is_fee_required and published_customisation.fixed_fee_amount:
            fixed_fee_amount = published_customisation.fixed_fee_amount.pence
        licence_name = (
            full_licence_interaction_context.interaction.licence_interaction_name
            if len(full_licence_interaction_context.interaction.display_title) < 1
            else full_licence_interaction_context.interaction.display_title
        )
        # base_licence_info_url = licence_lookup_service.get_licence_url(
        #     full_licence_interaction_context.licence, full_licence_interaction_context.authority
        # )
        context = {
            "authority_name": full_licence_interaction_context.authority.full_name.title(),
            "licence_name": licence_name,
            "interation_sub_id": interation_sub_id,
            "interaction_id": interaction_id,
            "is_fee_required": published_customisation.is_fee_required,
            "fee_amount": None if fixed_fee_amount == 0 else pence_to_pounds(fixed_fee_amount),
            "steps": 4 if published_customisation.is_fee_required else 3,
            "authority_slug": full_licence_interaction_context.authority.url_slug,
            "licence_slug": full_licence_interaction_context.licence.url_slug,
            "supporting_documents": published_customisation.supporting_document_definitions,
            "general_info_url": published_customisation.guidance_url,
            "legislation_info_url": "testurl",
        }
        context.update({"step": 1})
        return render(request, "citizen_frontend/licence_introduction_page.html", context)
    except Exception as e:
        raise Http404("Incorrect licence, or authority does not exist") from e


def submit_form(request, licence_slug: str, authority_slug: str, interaction_id: str, interation_sub_id: int):
    try:
        full_licence_interaction_context = licence_lookup_service.get_licence_interaction_context(
            authority_slug, licence_slug, interaction_id, interation_sub_id
        )
        if not full_licence_interaction_context:
            raise Http404("Incorrect licence, or authority does not exist") from None
        # TODO if handled by gov
        # if full_licence_interaction_context.licence_detail.handled_by_gov
        published_customisation = interaction_customisation_repository.find_published_customisation(
            authority_slug,
            full_licence_interaction_context.licence.licence_code,
            full_licence_interaction_context.interaction.interaction_id,
            full_licence_interaction_context.interaction.interaction_sub_id,
        )
        if not published_customisation:
            # TODO this actually checks to see if a licence has been suspended or something
            raise Http404("Incorrect licence, or authority does not exist") from None
        fixed_fee_amount = 0
        if published_customisation.is_fee_required and published_customisation.fixed_fee_amount:
            fixed_fee_amount = published_customisation.fixed_fee_amount.pence
        licence_name = (
            full_licence_interaction_context.interaction.licence_interaction_name
            if len(full_licence_interaction_context.interaction.display_title) < 1
            else full_licence_interaction_context.interaction.display_title
        )
        # base_licence_info_url = licence_lookup_service.get_licence_url(
        #     full_licence_interaction_context.licence, full_licence_interaction_context.authority
        # )
        context = {
            "authority_name": full_licence_interaction_context.authority.full_name.title(),
            "licence_name": licence_name,
            "interation_sub_id": interation_sub_id,
            "interaction_id": interaction_id,
            "is_fee_required": published_customisation.is_fee_required,
            "fee_amount": None if fixed_fee_amount == 0 else pence_to_pounds(fixed_fee_amount),
            "steps": 4 if published_customisation.is_fee_required else 3,
            "authority_slug": full_licence_interaction_context.authority.url_slug,
            "licence_slug": full_licence_interaction_context.licence.url_slug,
            "supporting_documents": published_customisation.supporting_document_definitions,
            "general_info_url": published_customisation.guidance_url,
            "legislation_info_url": "testurl",
        }
        context.update({"step": 2})

        if request.method == "POST":
            form = ApplicationSubmissionForm(
                request.POST,
                request.FILES,
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


def pence_to_pounds(pence: int) -> str:
    pounds = int(pence / 100)
    return f"£{pounds}.00"
