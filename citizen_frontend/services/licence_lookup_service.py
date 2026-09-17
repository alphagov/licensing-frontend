import os
from dataclasses import dataclass

from common.models.authorities import Authority, LicenceDetails
from common.models.interaction_customisations import Customisation
from common.models.licences import Licence, LicenceInteraction
from common.models.shared_models import PaymentAmount

import citizen_frontend.api.repository.authority_repository as authority_repository
import citizen_frontend.api.repository.licence_repository as licence_repository
from citizen_frontend.api.utils import INTERACTION_ID_WORD_MAPPING, INTERACTION_WORD_MAPPING
from citizen_frontend.enums.payment_type import PaymentType


@dataclass(frozen=True)
class LicenceContext:
    authority: Authority
    licence: Licence
    interaction: LicenceInteraction
    licence_detail: LicenceDetails


# previously lookupLicence
def get_licence_interaction_context(
    authority_url_slug: str, licence_url_slug: str, interaction: str, interaction_sub_id: int
) -> LicenceContext | None:

    authority = authority_repository.find_authority_by_url_slug(authority_url_slug)
    licence = licence_repository.get_licence_by_url_slug(licence_url_slug)
    if authority is None or licence is None:
        return None
    interaction_id = INTERACTION_WORD_MAPPING.get(interaction)
    if interaction_id is None:
        return None
    interaction_object = licence.find_interaction(interaction_id, interaction_sub_id)
    licence_detail = authority.find_licence_detail(licence.licence_code)
    if licence_detail is None or interaction_object is None:
        return None
    licence_context = LicenceContext(authority, licence, interaction_object, licence_detail)

    return licence_context


def get_licence_authority_and_interactions(licence_code: str):
    pass


def licence_authorities_and_interactions_by_snac_code(licence_code: str, snac_code: str):
    pass


def get_licence_url(licence_interaction: LicenceInteraction, licence: Licence, authority: Authority, uses_gov_uk: bool):
    if uses_gov_uk:
        interaction = INTERACTION_ID_WORD_MAPPING.get(licence_interaction.interaction_id, "")
        return (
            f"{os.getenv('BASE_URL', '')}/apply-for-a-licence/{licence.url_slug}/{authority.url_slug}/"
            f"{interaction}-{licence_interaction.interaction_sub_id}"
        )
    matched_licence_details = [
        licence_detail
        for licence_detail in authority.licence_details
        if licence_detail.licence_code == licence.licence_code
    ]
    if not matched_licence_details:
        return ""
    return matched_licence_details[0].authority_url


def get_payment_info_from_customisation(customisation: Customisation) -> tuple[PaymentType, PaymentAmount | None]:
    if not customisation.is_fee_required:
        return PaymentType.NONE, None

    if customisation.fixed_fee_amount and customisation.fixed_fee_amount.pence > 0:
        return PaymentType.FIXED_FEE, customisation.fixed_fee_amount

    return PaymentType.VARIABLE_FEE, None
