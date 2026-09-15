import os

from common.models.authorities import Authority
from common.models.interaction_customisations import Customisation
from common.models.licences import Licence, LicenceInteraction
from common.models.shared_models import PaymentAmount

from citizen_frontend.api.models.api_responses import LicenceAuthoritiesAndInteractionsResponse
from citizen_frontend.api.repository import licence_repository
from citizen_frontend.api.utils import INTERACTION_ID_WORD_MAPPING
from citizen_frontend.enums.payment_type import PaymentType
from citizen_frontend.services import authority_service


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
    licence = licence_repository.get_licence_by_licence_code(licence_code)
    if not licence:
        return "Licence " + licence_code + " doesn't exist"

    authorities = get_authorities(licence, snac_code)
    if not authorities:
        return f"No authorities found for the licence {licence.licence_code}" + (
            f" and for the SNAC/GSS Code {snac_code}" if snac_code else ""
        )

    is_location_specific = any(
        authority.snac_codes or not set(licence.administrative_area.countries).issubset(authority.countries)
        for authority in authorities
    )

    issuing_authorities = []

    return LicenceAuthoritiesAndInteractionsResponse(
        is_location_specific=is_location_specific,
        is_offered_by_county=licence.is_offered_by_county,
        geographical_availability=licence.administrative_area.countries,
        issuing_authorities=issuing_authorities,
    )


def get_authorities(licence: Licence, snac_code: str | None) -> list[Authority] | None:
    if snac_code:
        authorities = authority_service.get_authorities_for_licence_with_geographical_locator(snac_code, licence)
    else:
        authorities = authority_service.get_authorities_for_licence(licence.licence_code)
    return authorities
