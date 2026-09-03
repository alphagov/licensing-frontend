import re

from common.models.licences import Licence

from citizen_frontend.api.repository.authority_repository import AuthorityRepository
from citizen_frontend.api.utils import COUNTRY_TO_GSS_CODE, COUNTRY_TO_SNAC_CODE


class AuthorityService:
    def __init__(self):
        self.authority_repository = AuthorityRepository()

    def get_authorities_for_licence(self, licence_code):
        return self.authority_repository.get_licence_offering_authorities_by_licence_code(licence_code=licence_code)

    def get_authorities_for_licence_with_geographical_locator(self, locator: str, licence: Licence):
        country = self.get_country_from_geographical_locator(locator=locator)

        if country in licence.administrative_area.countries:
            self.get_authorities_for_licence(licence_code=licence.licence_code)

    @staticmethod
    def get_country_from_geographical_locator(locator: str):
        for key, value in COUNTRY_TO_SNAC_CODE.items():
            if locator in value:
                return key

        for key, value in COUNTRY_TO_GSS_CODE.items():
            if re.match(value, locator):
                return key

        return None
