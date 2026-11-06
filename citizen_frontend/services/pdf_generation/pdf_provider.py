import os
from abc import ABC, abstractmethod
from io import BytesIO

from common.models.authority import Authority
from common.models.department import Department
from common.models.interaction_customisation import Customisation
from common.models.licence import Licence, LicenceInteraction
from django.template.loader import render_to_string

from citizen_frontend.exceptions import PDFGenerationGeneralError, PDFProviderUnavailableError


class PdfProvider(ABC):
    @abstractmethod
    def generate_pdf(self, *args, **kwargs):
        pass

    @abstractmethod
    def flatten_pdf(self):
        pass


class APTOPdfProvider(PdfProvider):
    def generate_pdf(
        self,
        authority: Authority,
        licence: Licence,
        customisation: Customisation,
        department: Department,
        return_url: str,
        interaction: LicenceInteraction,
    ):
        pass

    def flatten_pdf(self):
        pass

    def create_xml_request(
        self,
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


class MockAPTOPdfProvider(PdfProvider):
    def generate_pdf(
        self,
        authority: Authority,
        licence: Licence,
        customisation: Customisation,
        department: Department,
        return_url: str,
        interaction: LicenceInteraction,
    ):
        if authority.name == "barnet":
            raise PDFGenerationGeneralError("Mocking general error with Barnet")

        if authority.name == "elmbridge":
            raise PDFProviderUnavailableError("Mocking PDF Generation unavailable response with Elmbridge")

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
