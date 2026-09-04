import os

from common.models.authorities import Authority
from common.models.licences import Licence, LicenceInteraction


class LicenceLookupService:
    def get_licence_authority_and_interactions(self, licence_code: str):
        pass

    def licence_authorities_and_interactions_by_snac_code(self, licence_code: str, snac_code: str):
        pass

    def get_base_licence_url(
        self, interaction: LicenceInteraction, licence: Licence, authority: Authority, uses_gov_uk: bool
    ):
        if uses_gov_uk:
            return f"{os.getenv('BASE_URL', '')}/apply-for-a-licence/{licence.url_slug}/{authority.url_slug}"
        matched_licence_details = [
            licence_detail
            for licence_detail in authority.licence_details
            if licence_detail.licence_code == licence.licence_code
        ]
        return matched_licence_details[0].authority_url
