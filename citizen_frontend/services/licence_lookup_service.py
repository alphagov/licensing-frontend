import os

from common.models.authorities import Authority
from common.models.interaction_customisations import Customisation
from common.models.licences import Licence, LicenceInteraction
from common.models.shared_models import PaymentAmount

from citizen_frontend.api.utils import INTERACTION_ID_WORD_MAPPING
from citizen_frontend.enums.payment_type import PaymentType


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


def get_authority_licence_and_interactions(licence_code: str, snac_code: str | None = None):
    return "Licence " + licence_code + " doesn't exist"
