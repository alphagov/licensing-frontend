import logging

from common.models.authority import Authority
from common.models.interaction_customisation import Customisation
from common.models.licence import Licence, LicenceInteraction
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from citizen_frontend.exceptions import FormNotFoundException
from citizen_frontend.repository.base_repo import DepartmentRepo
from citizen_frontend.services.pdf_generation.pdf_provider import get_pdf_provider

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PdfGenerator:
    def __init__(self):
        self.pdf_provider = get_pdf_provider()
        self.department_repository = DepartmentRepo()

    def handle_request(
        self, authority: Authority, licence: Licence, interaction: LicenceInteraction, customisation: Customisation
    ):
        try:
            department = self.department_repository.get_by_id(department_id=customisation.department)

            return_url = self.create_return_url(
                authority_slug=authority.url_slug,
                licence_slug=licence.url_slug,
                interaction_id=interaction.interaction_id,
                interaction_sub_id=interaction.interaction_sub_id,
            )

            file_path = self.create_download_file_path(authority=authority, interaction=interaction)

            application_pdf_form = self.pdf_provider.request_pdf_form(
                authority=authority,
                licence=licence,
                department=department,
                customisation=customisation,
                return_url=return_url,
                interaction=interaction,
            )

            return application_pdf_form, file_path

        except ObjectDoesNotExist as e:
            logger.error(
                "Department not found for authority: %s, agencyId= %s, departmentId= %s",
                authority.name,
                authority.agency_id,
                customisation.department,
            )
            raise FormNotFoundException("Department not found") from e

    @staticmethod
    def create_return_url(authority_slug, licence_slug, interaction_id, interaction_sub_id):
        # TODO do we need to include base URL here, only has the path
        return reverse(
            "begin_application_steps",
            kwargs={
                "authority_slug": authority_slug,
                "licence_slug": licence_slug,
                "interaction_id": interaction_id,
                "interaction_sub_id": interaction_sub_id,
            },
        )

    @staticmethod
    def create_download_file_path(authority: Authority, interaction: LicenceInteraction):
        return f"{authority.name.replace(' ', '_')}_{interaction.licence_interaction_name.replace(' ', '_')}.pdf"
