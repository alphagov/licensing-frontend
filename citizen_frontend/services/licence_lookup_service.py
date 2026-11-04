import logging
import os
from collections import defaultdict

from common.enums.interaction_id_codes import InteractionIdCodes
from common.models.authority import Authority, ContactInformation, LicenceDetail
from common.models.interaction_customisation import Customisation
from common.models.licence import Licence, LicenceInteraction
from django.core.exceptions import ObjectDoesNotExist
from pydantic import ValidationError

from citizen_frontend.api.models.api_responses import (
    AuthorityContactInformation,
    AuthorityInteraction,
    IssuingAuthority,
    LicenceAuthoritiesAndInteractionsResponse,
)
from citizen_frontend.api.utils import INTERACTION_ID_WORD_MAPPING
from citizen_frontend.enums.licence_interactions import LicenceInteractions
from citizen_frontend.enums.payment_type import PaymentType
from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError, LicenceLookupError
from citizen_frontend.repository.authority_repository import AuthorityRepository
from citizen_frontend.repository.interaction_customisation_repository import CustomisationRepository
from citizen_frontend.repository.licence_repository import LicenceRepository
from citizen_frontend.services.authority_service import AuthorityService
from citizen_frontend.services.licence_service import LicenceService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LicenceLookupService:
    def __init__(self):
        self.licence_service = LicenceService()
        self.authority_service = AuthorityService()
        self.licence_repository = LicenceRepository()
        self.authority_repository = AuthorityRepository()
        self.interaction_customisation_repository = CustomisationRepository()

    # previously lookupLicence
    def get_licence_interaction_context(
        self, authority_url_slug: str, licence_url_slug: str, interaction: InteractionIdCodes, interaction_sub_id: int
    ) -> tuple[Licence, Authority, LicenceInteraction, LicenceDetail]:
        licence = self.licence_repository.get_licence_by_url_slug(licence_url_slug)
        authority = self.authority_repository.find_authority_by_url_slug(authority_url_slug)
        if not authority:
            logger.error("No authority found for %s", authority_url_slug)
            raise ObjectDoesNotExist("Authority not found")
        licence_detail = self.authority_service.find_licence_detail(authority, licence.licence_code)
        if not licence_detail:
            logger.error("Failed to find licence detail for %s in %s", licence.licence_code, authority)
            raise ObjectDoesNotExist("Licence detail not found")
        interaction_object = self.licence_service.find_interaction(licence, interaction, interaction_sub_id)
        if not interaction_object:
            logger.error(
                "Missing interaction for licence: %s, interaction: %s and interaction_sub_id: %s",
                licence,
                interaction,
                interaction_sub_id,
            )
            raise ObjectDoesNotExist("Interaction not found")

        return licence, authority, interaction_object, licence_detail

    def get_licence_authorities_and_interactions(self, licence_code: str, snac_code: str | None = None):
        try:
            licence = self.licence_repository.get_licence_by_licence_code(licence_code)
            if not licence:
                raise LicenceLookupError(f"Licence {licence_code} doesn't exist")

            authorities = self.get_authorities(licence, snac_code)
            if not authorities:
                message = f"No authorities found for the licence {licence.licence_code}" + (
                    f" and for the SNAC/GSS Code {snac_code}" if snac_code else ""
                )
                raise LicenceLookupError(message)

            is_location_specific = self.check_if_location_specific(authorities, licence)

            issuing_authorities = (
                []
                if is_location_specific and not snac_code
                else [
                    self.get_authority_licence_interaction_details(authority=authority, licence=licence)
                    for authority in authorities
                ]
            )

            return LicenceAuthoritiesAndInteractionsResponse(
                is_location_specific=is_location_specific,
                is_offered_by_county=licence.is_offered_by_county,
                geographical_availability=licence.administrative_area.countries,
                issuing_authorities=issuing_authorities,
            )
        except (DataIntegrityError, DocumentDBError) as e:
            raise LicenceLookupError(e.args[0]) from e
        except ValidationError as e:
            logger.error("Failed to build: %s", e.title)
            logger.error(e)
            raise LicenceLookupError(f"{e.title} validation error") from e

    def get_authority_licence_interaction_details(self, authority: Authority, licence: Licence) -> IssuingAuthority:
        interactions = self.build_authority_interactions(authority, licence)

        contact_details = authority.contact_details
        postal_address = self.format_postal_address(contact_details)

        return IssuingAuthority(
            authority_name=authority.full_name,
            authority_slug=authority.url_slug,
            authority_contact=AuthorityContactInformation(
                website=authority.authority_url if authority.authority_url else "",
                email=contact_details.email if contact_details.email else "",
                phone=contact_details.phone_number if contact_details.phone_number else "",
                address=postal_address,
            ),
            authority_interactions=interactions,
        )

    def build_authority_interactions(
        self, authority: Authority, licence: Licence
    ) -> dict[str, list[AuthorityInteraction]]:
        logger.info("Building AuthorityInteractions for: %s, %s", authority.id, licence.id)
        licence_details = next(
            (ld for ld in authority.licence_details if ld.licence_code == licence.licence_code), None
        )
        uses_gov_uk = getattr(licence_details, "using_gov_uk", False)
        offered_by_auth = getattr(licence_details, "offered_by_authority", False)

        grouped_interactions = self.group_interactions(licence)

        result = defaultdict(list)
        for interaction_type, interactions in grouped_interactions.items():
            for interaction in interactions:
                customisation = self.interaction_customisation_repository.find_published_customisation(
                    authority.url_slug, licence.licence_code, interaction.interaction_id, interaction.interaction_sub_id
                )
                interaction_url = self.get_licence_url(interaction, licence, authority, uses_gov_uk)
                uses_auth_url = bool(not uses_gov_uk and offered_by_auth and interaction_url)

                logger.info("Retrieving payment information")
                payment_type, payment_amount = self.get_payment_info_from_customisation(customisation)

                result[interaction_type].append(
                    AuthorityInteraction(
                        url=interaction_url,
                        uses_licensify=uses_gov_uk,
                        uses_authority_url=uses_auth_url,
                        description=interaction.licence_interaction_name,
                        payment=payment_type,
                        payment_amount=payment_amount,
                        introduction_text=customisation.introduction_text if customisation else "",
                    )
                )
        return result

    def get_licence_url(
        self, licence_interaction: LicenceInteraction, licence: Licence, authority: Authority, uses_gov_uk: bool
    ):
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

    def get_payment_info_from_customisation(
        self, customisation: Customisation | None
    ) -> tuple[PaymentType, str | None]:
        if not customisation or not customisation.is_fee_required:
            return PaymentType.NONE, None

        if customisation.fixed_fee_amount and customisation.fixed_fee_amount.pence > 0:
            return PaymentType.FIXED_FEE, customisation.fixed_fee_amount.format_to_string_in_pounds

        return PaymentType.VARIABLE_FEE, None

    def format_postal_address(self, contact_details: ContactInformation) -> str:
        address_lines = [
            contact_details.line_one,
            contact_details.line_two,
            contact_details.line_three,
            contact_details.city,
            contact_details.post_code,
        ]
        return "\n".join(line for line in address_lines if line)

    def check_if_location_specific(self, authorities: list[Authority], licence: Licence) -> bool:
        return any(
            authority.snac_codes or not set(licence.administrative_area.countries).issubset(authority.countries)
            for authority in authorities
        )

    def get_authorities(self, licence: Licence, snac_code: str | None) -> list[Authority] | None:
        if snac_code:
            authorities = self.authority_service.get_authorities_for_licence_with_geographical_locator(
                snac_code, licence
            )
        else:
            authorities = self.authority_service.get_authorities_for_licence(licence.licence_code)
        return authorities

    def group_interactions(self, licence: Licence) -> dict[str, list[LicenceInteraction]]:
        logger.info("Grouping interactions for licence: %s", licence.id)
        grouped_interactions = defaultdict(list)
        for interaction in licence.licence_interactions:
            interaction_type = INTERACTION_ID_WORD_MAPPING.get(
                interaction.interaction_id, LicenceInteractions.UNKNOWN
            ).value
            grouped_interactions[interaction_type].append(interaction)
        return grouped_interactions
