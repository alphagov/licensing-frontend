import os
from abc import ABC, abstractmethod
from enum import StrEnum
from io import BytesIO

import requests
from common.models.authority import Authority
from common.models.department import Department
from common.models.interaction_customisation import Customisation
from common.models.licence import Licence, LicenceInteraction
from django.template.loader import render_to_string
from requests import HTTPError
from requests.adapters import HTTPAdapter

from citizen_frontend.exceptions import PDFGenerationGeneralError, PDFProviderUnavailableError
from citizen_frontend.repository.base_repo import SettingsRepo


class AptoStatuses(StrEnum):
    AVAILABLE = "available"
    DOWNLOAD_ONLY = "onlyForDownload"
    NOT_AVAILABLE = "notAvailable"


class PdfProvider(ABC):
    @abstractmethod
    def request_pdf_form(self, *args, **kwargs):
        pass

    @abstractmethod
    def flatten_pdf(self):
        pass


class APTOPdfProvider(PdfProvider):
    def __init__(self):
        self.settings_repo = SettingsRepo()

    def request_pdf_form(
        self,
        authority: Authority,
        licence: Licence,
        customisation: Customisation,
        department: Department,
        return_url: str,
        interaction: LicenceInteraction,
    ):
        try:
            if not self.get_apto_pdf_status_setting():
                # TODO check what message is currently being used in the codebase
                raise PDFProviderUnavailableError("APTO PDF is unavailable for download")

            session = requests.Session()

            adapter = HTTPAdapter(
                pool_connections=int(os.getenv("APTO_MAX_HTTP_CONNECTIONS", 126)),
                pool_maxsize=int(os.getenv("APTO_MAX_CONNECTIONS_PER_ROUTE", 16)),
                pool_block=True,
            )
            # TODO double check timeout and pool connections correspond correctly.

            session.mount("https://", adapter)

            xml_bytes = self.create_xml_request(
                licence, authority, customisation, department, interaction, return_url
            ).encode("utf-8")

            byte_stream = BytesIO(xml_bytes)

            response = session.post(
                url=f"{os.getenv('APTO_REQUEST_BASE_URL')}/Licence/{interaction.form.form_ref_number}",
                files={"AttachedData": ("customisationFile.xml", byte_stream, "text/xml")},
                timeout=(int(os.getenv("APTO_CONNECTION_TIMEOUT", 3.05)), int(os.getenv("APTO_SOCKET_TIMEOUT", 3))),
            )

            response.raise_for_status()

        #     TODO extract content from response as steam?
        except HTTPError as e:
            raise PDFGenerationGeneralError(f"Received error from APTO: {e}") from e

    def get_apto_pdf_status_setting(self) -> bool:
        status = self.settings_repo.get_setting(key="aptoStatus")
        return status == AptoStatuses.AVAILABLE or status == AptoStatuses.DOWNLOAD_ONLY

    @staticmethod
    def create_xml_request(
        licence: Licence,
        authority: Authority,
        customisation: Customisation,
        department: Department,
        interaction: LicenceInteraction,
        return_url: str,
    ):

        modified_declarations = (
            [declaration.replace("&pound;", "\u00a3") for declaration in customisation.declarations]
            if customisation.declarations
            else None
        )
        modified_calculations = (
            [calculation.replace("&pound;", "\u00a3") for calculation in customisation.fee_calculation_instructions]
            if customisation.fee_calculation_instructions
            else None
        )

        fee_amount = (
            customisation.fixed_fee_amount.format_to_string_in_pounds
            if customisation.is_fee_required and customisation.fixed_fee_amount
            else "0"
        )

        context = {
            "return_url": return_url,
            "authority": authority,
            "department": department,
            "interaction": interaction,
            "licence": licence,
            "customisation": customisation,
            "fixed_fee_amount": fee_amount,
            "modified_declarations": modified_declarations,
            "modified_calculations": modified_calculations,
        }
        return render_to_string("citizen_frontend/pdf_generation/apto_template.xml", context)

    def flatten_pdf(self):
        pass


class MockAPTOPdfProvider(PdfProvider):
    def request_pdf_form(
        self,
        authority: Authority,
        licence: Licence,
        customisation: Customisation,
        department: Department,
        return_url: str,
        interaction: LicenceInteraction,
    ):
        if authority.name == "Barnet":
            raise PDFGenerationGeneralError("Mocking general error with Barnet")

        if authority.name == "York":
            raise PDFProviderUnavailableError("Mocking PDF Generation unavailable response with York")

        if customisation.is_fee_required and customisation.fee_calculation_instructions:
            return self.create_buffer("citizen_frontend/services/resources/test_forms/temporary-event-notice.pdf")
        else:
            return self.create_buffer("citizen_frontend/services/resources/test_forms/fish_dealers_licence.pdf")

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
