import os
from abc import ABC, abstractmethod
from io import BytesIO

from common.models.authority import Authority
from common.models.department import Department
from common.models.interaction_customisation import Customisation
from common.models.licence import Licence, LicenceInteraction
from django.template.loader import render_to_string
from django.urls import reverse

from citizen_frontend.repository.base_repo import DepartmentRepo
from citizen_frontend.services import licence_lookup_service


class PdfProvider(ABC):
    @abstractmethod
    def generate_pdf(self, *args, **kwargs):
        pass

    @abstractmethod
    def flatten_pdf(self):
        pass


"mongodb://docdb:password@localhost:10260?tls=true&tlsAllowInvalidCertificates=true"


class APTOPdfProvider(PdfProvider):
    def generate_pdf(
        self,
        authority: Authority,
        licence: Licence,
        customisation: Customisation,
        department: Department,
        return_url: str,
    ):
        pass

    def flatten_pdf(self):
        pass

    def create_xml_request(self, licence: Licence, authority: Authority, customisation: Customisation, return_url: str):
        context = {
            "return_url": return_url,
        }
        return render_to_string("citizen_frontend/pdf_generation/apto_template.xml", context)


class MockAPTOPdfProvider(PdfProvider):
    def generate_pdf(
        self,
        authority: Authority,
        licence: Licence,
        customisation: Customisation,
        department: Department,
        return_url: str,
    ):
        if customisation.is_fee_required and customisation.fee_calculation_instructions:
            return self.create_buffer("citizen_frontend/services/resources/test_forms/fish_dealers_licence.pdf")
        else:
            return self.create_buffer("citizen_frontend/services/resources/test_forms/temporary-event-notice.pdf")

    @staticmethod
    def create_buffer(file_path):
        with open(file_path, "rb") as f:
            buffer = BytesIO(f.read())
            buffer.seek(0)
            return buffer

    def flatten_pdf(self):
        pass


def get_pdf_provider():
    return (
        MockAPTOPdfProvider() if os.getenv("IS_PRODUCTION", "true").lower() not in ["true", "1"] else APTOPdfProvider()
    )


class PdfGenerator:
    def __init__(self):
        self.pdf_provider = get_pdf_provider()
        self.licence_lookup_service = licence_lookup_service
        self.department_repository = DepartmentRepo()

    def handle_request(self, authority_slug, licence_slug, licence_code, interaction_id, interaction_sub_id):
        licence, authority, interaction, _ = self.licence_lookup_service.get_licence_interaction_context(
            authority_url_slug=authority_slug,
            licence_url_slug=licence_slug,
            interaction=interaction_id,
            interaction_sub_id=interaction_sub_id,
        )

        published_customisation = (
            self.licence_lookup_service.interaction_customisation_repository.find_published_customisation(
                authority_url_slug=authority_slug,
                licence_code=licence_code,
                interaction_id=interaction_id,
                interaction_sub_id=interaction_sub_id,
            )
        )

        department = self.department_repository.get_by_id(department_id=published_customisation.department)

        return_url = self.create_return_url(
            authority_slug=authority_slug,
            licence_slug=licence_slug,
            interaction_id=interaction_id,
            interaction_sub_id=interaction_sub_id,
        )

        file_path = self.create_download_file_path(authority=authority, interaction=interaction)

        application_pdf_form = self.pdf_provider.generate_pdf(
            authority=authority,
            licence=licence,
            department=department,
            customisation=published_customisation,
            return_url=return_url,
        )

        return application_pdf_form, file_path

    @staticmethod
    def create_return_url(authority_slug, licence_slug, interaction_id, interaction_sub_id):
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


# context = {
#         'book': {
#             'id': 'BK101',
#             'title': 'Django for Beginners',
#             'author': 'William S. Vincent',
#             'price': 39.99,
#             'currency': 'USD',
#             'date': '2026-01-15'
#         },
#         'items': [
#             {'code': 'A1', 'name': 'Widget X', 'qty': 10},
#             {'code': 'B2', 'name': 'Widget Y', 'qty': 5},
#         ]
#     }
#
#     # Render the template to a string
#     xml_content = render_to_string('my_template.xml', context)
