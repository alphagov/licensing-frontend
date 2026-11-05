import xml.etree.ElementTree as ET

import pytest
from conftest import TEST_AUTHORITY, TEST_CUSTOMISATION_FIXED_FEE, TEST_LICENCE

from citizen_frontend.services.pdf_generation.pdf_provider import APTOPdfProvider


@pytest.fixture
def apto_pdf_provider():
    yield APTOPdfProvider()


def test_apto_pdf_provider_creates_apto_request_xml_with_correct_structure(apto_pdf_provider):
    namespaces = {
        "ns": "http://www.aptosolutions.co.uk/businesslink/psc/common/2.3",
        "common": "http://www.aptosolutions.co.uk/businesslink/psc/common/2.3",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    xml_request = apto_pdf_provider.create_xml_request(
        licence=TEST_LICENCE,
        authority=TEST_AUTHORITY,
        customisation=TEST_CUSTOMISATION_FIXED_FEE,
        return_url="some return url",
        department={"help_email": "some email", "help_phone": "some phone number"},
        interaction=TEST_LICENCE.licence_interactions[0],
    )
    # TODO replace department with an instance of Department model

    root = ET.fromstring(xml_request)

    assert root.find("ns:CommonSections/ns:returnURL", namespaces).text == "some return url"
    assert root.find("ns:CommonSections/ns:Branding/ns:logoUri", namespaces).text == TEST_AUTHORITY.encoded_image
    assert root.find("ns:CommonSections/ns:Branding/ns:altText", namespaces).text == TEST_AUTHORITY.name
    assert root.find("ns:CommonSections/ns:Branding/ns:colour", namespaces).text == "FFFFFF"
    assert root.find("ns:CommonSections/ns:Branding/ns:HelpContact/ns:emailAddress", namespaces).text == "some email"
    assert (
        root.find("ns:CommonSections/ns:Branding/ns:HelpContact/ns:telephone", namespaces).text == "some phone number"
    )
    assert root.find("ns:CommonSections/ns:FormMetaData/ns:transactionId", namespaces).text == "Not Currently In Use"
    assert (
        root.find("ns:CommonSections/ns:FormMetaData/ns:formId", namespaces).text
        == TEST_LICENCE.licence_interactions[0].form.form_ref_number
    )
    # TODO this is the xml request from common/app/uk/gov/gds/licensing/pdf/PdfGenerationRequest.scala
    #   this takes in auth, licence, interaction, customisation, department, return url


def test_apto_pdf_provider_checks_apto_availability():
    pass


def test_apto_pdf_provider_sends_post_request_to_apto_with_correct_body():
    pass


def test_apto_pdf_provider_throws_error_on_non_200_response_from_apto_request():
    pass


def test_apto_not_found():
    # TODO frontend/app/uk/gov/gds/licensing/frontend/controllers/FormProxyController.scala
    #  Render not found page, should happen in the controller layer but currently to the form proxy does this
    #  and the pdf generator throws this, custom errors?
    pass


def test_apto_not_published():
    # TODO frontend/app/uk/gov/gds/licensing/frontend/controllers/FormProxyController.scala
    # Render contact page, should happen in the view controller layer,
    # PDF generator throws thsi too
    pass


def test_apto_not_available():
    pass
