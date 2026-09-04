import os

from common.models.authorities import Authority
from common.models.licences import Licence


class LicenceLookupService:
    def get_licence_authority_and_interactions(self, licence_code: str):
        pass

    def licence_authorities_and_interactions_by_snac_code(self, licence_code: str, snac_code: str):
        pass

    def get_base_licence_url(self, licence: Licence, authority: Authority, uses_gov_uk: bool):
        return f"{os.getenv('BASE_URL', '')}/apply-for-a-licence/{licence.url_slug}/{authority.url_slug}"
