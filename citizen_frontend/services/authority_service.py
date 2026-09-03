import logging
import re

from common.models.authorities import Authority
from common.models.licences import Licence

from citizen_frontend.api.repository.authority_repository import AuthorityRepository
from citizen_frontend.api.utils import COUNTRY_TO_GSS_CODE, COUNTRY_TO_SNAC_CODE

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AuthorityService:
    def __init__(self):
        self.authority_repository = AuthorityRepository()

    def get_authorities_for_licence(self, licence_code):
        return self.authority_repository.get_licence_offering_authorities_by_licence_code(licence_code=licence_code)

    def get_authorities_for_licence_with_geographical_locator(
        self, locator: str, licence: Licence
    ) -> list[Authority] | None:
        country = self.get_country_from_geographical_locator(locator=locator)
        # need to check what happens if no country => snac or gss incorrect..
        if not country:
            return None

        if country not in licence.administrative_area.countries:
            logger.info("%s not present in licence administrative area for licence: %s", country, licence.licence_code)
            return None

        logger.info("Retrieving authorities that offer licence for licence code: %s", licence.licence_code)
        authorities = self.get_authorities_for_licence(licence_code=licence.licence_code)

        return [
            authority
            for authority in authorities
            if self.check_authority_covers_location(authority=authority, locator=locator, country=country)
        ]

    @staticmethod
    def get_country_from_geographical_locator(locator: str) -> str | None:
        logger.info("Retrieving country from geographical locator")
        for key, value in COUNTRY_TO_SNAC_CODE.items():
            if locator in value:
                return key.value

        for key, value in COUNTRY_TO_GSS_CODE.items():
            if re.match(value, locator):
                return key.value

        logger.info("No country found for locator: %s", locator)
        return None

    @staticmethod
    def check_authority_covers_location(authority: Authority, locator: str, country: str) -> bool:
        logger.info("Checking authority: %s covers location: %s and country: %s", authority.name, locator, country)

        is_locator_valid = locator in authority.snac_codes or not authority.snac_codes
        is_country_present = country in authority.countries

        if not is_locator_valid or not is_country_present:
            logger.info("%s does not cover location: %s and country: %s", authority.name, locator, country)
            return False

        logger.info("%s covers location: %s and country: %s", authority.name, locator, country)
        return True
