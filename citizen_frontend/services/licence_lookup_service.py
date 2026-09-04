import os

from common.models.authorities import Authority
from common.models.licences import Licence, LicenceInteraction

from citizen_frontend.api.utils import INTERACTION_ID_WORD_MAPPING


class LicenceLookupService:
    def get_licence_authority_and_interactions(self, licence_code: str):
        pass

    def licence_authorities_and_interactions_by_snac_code(self, licence_code: str, snac_code: str):
        pass

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
