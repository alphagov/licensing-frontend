import os
import xml.etree.ElementTree as ET
from copy import deepcopy
from io import BytesIO

import pytest
import requests
from conftest import (
    TEST_AUTHORITY,
    TEST_CUSTOMISATION_FIXED_FEE,
    TEST_CUSTOMISATION_NO_FEE,
    TEST_CUSTOMISATION_VARIABLE_FEE,
    TEST_DEPARTMENT,
    TEST_LICENCE,
)
from requests import HTTPError

from citizen_frontend.exceptions import PDFGenerationGeneralError, PDFProviderUnavailableError
from citizen_frontend.services.pdf_generation.pdf_provider import APTOPdfProvider, AptoStatuses


@pytest.fixture
def mock_session(mocker):
    mocked_class = mocker.patch("citizen_frontend.services.pdf_generation.pdf_provider.requests.Session")
    session = mocked_class.return_value
    yield session


@pytest.fixture
def apto_pdf_provider(mocker):
    pdf_provider = APTOPdfProvider()

    yield pdf_provider


namespaces = {
    "ns": "http://www.aptosolutions.co.uk/businesslink/psc/common/2.3",
    "common": "http://www.aptosolutions.co.uk/businesslink/psc/common/2.3",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


def test_apto_pdf_provider_happy_path(apto_pdf_provider, mocker, mock_session):
    mocker.patch.object(apto_pdf_provider, "is_apto_available", return_value=True)

    session = requests.Session()
    mocker.patch.object(apto_pdf_provider, "configure_apto_session", return_value=session)
    mock_post = mock_session.post

    with open("citizen_frontend/services/resources/test_forms/temporary-event-notice.pdf", "rb") as f:
        buffer = BytesIO(f.read())
        buffer.seek(0)

    mock_post.return_value.status_code = 200
    mock_post.return_value.content = buffer

    expected_xml_request_body = apto_pdf_provider.create_xml_request(
        authority=TEST_AUTHORITY,
        licence=TEST_LICENCE,
        customisation=TEST_CUSTOMISATION_FIXED_FEE,
        interaction=TEST_LICENCE.licence_interactions[0],
        return_url="",
        department=TEST_DEPARTMENT,
    ).encode("utf-8")

    xml_stream = BytesIO(expected_xml_request_body)
    mocker.patch("citizen_frontend.services.pdf_generation.pdf_provider.BytesIO", return_value=xml_stream)

    actual = apto_pdf_provider.request_pdf_form(
        authority=TEST_AUTHORITY,
        licence=TEST_LICENCE,
        department=TEST_DEPARTMENT,
        customisation=TEST_CUSTOMISATION_FIXED_FEE,
        interaction=TEST_LICENCE.licence_interactions[0],
        return_url="",
    )

    apto_pdf_provider.is_apto_available.assert_called()
    apto_pdf_provider.configure_apto_session.assert_called()
    mock_post.assert_called_with(
        url=f"{os.getenv('APTO_REQUEST_BASE_URL')}/Licence/{TEST_LICENCE.licence_interactions[0].form.form_ref_number}",
        files={
            "AttachedData": ("customisationFile.xml", xml_stream, "text/xml"),
        },
        timeout=(float(os.getenv("APTO_CONNECTION_TIMEOUT", 3.05)), int(os.getenv("APTO_SOCKET_TIMEOUT", 3))),
    )

    assert actual == buffer


def test_apto_pdf_provider_throws_error_apto_not_available(apto_pdf_provider, mocker):
    mocker.patch.object(apto_pdf_provider, "is_apto_available", return_value=False)

    with pytest.raises(PDFProviderUnavailableError):
        apto_pdf_provider.request_pdf_form(
            authority=TEST_AUTHORITY,
            licence=TEST_LICENCE,
            department=TEST_DEPARTMENT,
            customisation=TEST_CUSTOMISATION_FIXED_FEE,
            interaction=TEST_LICENCE.licence_interactions[0],
            return_url="",
        )


def test_apto_pdf_provider_uses_correct_session(apto_pdf_provider):

    session = apto_pdf_provider.configure_apto_session()
    adapter = session.get_adapter("https://example.com")

    assert adapter._pool_connections == 1
    assert adapter._pool_maxsize == 16
    assert adapter._pool_block


def test_apto_pdf_provider_throws_error_on_non_200_response_from_apto_request(apto_pdf_provider, mock_session, mocker):
    mocker.patch.object(apto_pdf_provider, "is_apto_available", return_value=True)
    mock_session.post.side_effect = HTTPError

    with pytest.raises(PDFGenerationGeneralError):
        apto_pdf_provider.request_pdf_form(
            authority=TEST_AUTHORITY,
            licence=TEST_LICENCE,
            department=TEST_DEPARTMENT,
            customisation=TEST_CUSTOMISATION_FIXED_FEE,
            interaction=TEST_LICENCE.licence_interactions[0],
            return_url="",
        )


def test_get_apto_pdf_status_setting_calls_settings_repo_with_correct_args(apto_pdf_provider, mocker):
    settings_repo = mocker.patch.object(apto_pdf_provider, "settings_repo")

    apto_pdf_provider.is_apto_available()

    settings_repo.get_setting.assert_called_with(key="aptoStatus")


def test_get_apto_pdf_status_setting_returns_false_apto_unavailable(apto_pdf_provider, mocker):
    mocker.patch.object(apto_pdf_provider, "settings_repo", return_value=AptoStatuses.NOT_AVAILABLE)

    actual = apto_pdf_provider.is_apto_available()

    assert not actual


def test_xml_request_should_contain_calculation_instructions_and_no_payment_element_for_a_licence_with_variable_fee(
    apto_pdf_provider,
):
    xml_request = apto_pdf_provider.create_xml_request(
        licence=TEST_LICENCE,
        authority=TEST_AUTHORITY,
        customisation=TEST_CUSTOMISATION_VARIABLE_FEE,
        return_url="some return url",
        department=TEST_DEPARTMENT,
        interaction=TEST_LICENCE.licence_interactions[0],
    )

    root = ET.fromstring(xml_request)

    assert root.find("ns:CommonSections/ns:PaymentDetails/ns:isFixedFee", namespaces) is None
    assert root.find("ns:CommonSections/ns:PaymentDetails/ns:isPayment", namespaces) is None
    assert len(root.findall("ns:CommonSections/ns:PaymentDetails/ns:Calculation", namespaces)) == len(
        TEST_CUSTOMISATION_VARIABLE_FEE.fee_calculation_instructions
    )


def test_xml_request_should_contain_not_return_url_section_if_no_return_url_has_been_provided(apto_pdf_provider):
    xml_request = apto_pdf_provider.create_xml_request(
        licence=TEST_LICENCE,
        authority=TEST_AUTHORITY,
        customisation=TEST_CUSTOMISATION_VARIABLE_FEE,
        return_url="",
        department=TEST_DEPARTMENT,
        interaction=TEST_LICENCE.licence_interactions[0],
    )

    root = ET.fromstring(xml_request)

    assert root.find("ns:CommonSections/ns:returnURL", namespaces) is None


def test_xml_request_should_not_contain_logo_section_if_no_logo_has_been_provided(apto_pdf_provider):
    xml_request = apto_pdf_provider.create_xml_request(
        licence=TEST_LICENCE,
        authority=TEST_AUTHORITY,
        customisation=TEST_CUSTOMISATION_VARIABLE_FEE,
        return_url="",
        department=TEST_DEPARTMENT,
        interaction=TEST_LICENCE.licence_interactions[0],
    )

    root = ET.fromstring(xml_request)

    assert root.find("ns:CommonSections/ns:Branding/ns:logoUri", namespaces) is None


def test_xml_request_should_contain_fixed_fee_section_with_0_as_amount_for_free_licence(apto_pdf_provider):
    xml_request = apto_pdf_provider.create_xml_request(
        licence=TEST_LICENCE,
        authority=TEST_AUTHORITY,
        customisation=TEST_CUSTOMISATION_NO_FEE,
        return_url="",
        department=TEST_DEPARTMENT,
        interaction=TEST_LICENCE.licence_interactions[0],
    )

    root = ET.fromstring(xml_request)

    assert root.find("ns:CommonSections/ns:PaymentDetails/ns:Payment", namespaces).text == "0"


def test_xml_request_should_not_contain_declaration_section_if_customisation_had_no_declarations_set(apto_pdf_provider):
    customisation_with_no_declarations = deepcopy(TEST_CUSTOMISATION_FIXED_FEE)
    customisation_with_no_declarations.declarations = []

    xml_request = apto_pdf_provider.create_xml_request(
        licence=TEST_LICENCE,
        authority=TEST_AUTHORITY,
        customisation=customisation_with_no_declarations,
        return_url="",
        department=TEST_DEPARTMENT,
        interaction=TEST_LICENCE.licence_interactions[0],
    )

    root = ET.fromstring(xml_request)

    assert root.findall("ns:CommonSections/ns:Declarations/ns:Declaration", namespaces) == []
    assert root.find("ns:CommonSections/ns:Declarations/ns:Declaration", namespaces) is None


def test_apto_pdf_provider_creates_apto_request_xml_with_correct_structure(apto_pdf_provider):
    authority_with_image = deepcopy(TEST_AUTHORITY)
    authority_with_image.encoded_image = "this is an encoded image"

    xml_request = apto_pdf_provider.create_xml_request(
        licence=TEST_LICENCE,
        authority=authority_with_image,
        customisation=TEST_CUSTOMISATION_FIXED_FEE,
        return_url="some return url",
        department=TEST_DEPARTMENT,
        interaction=TEST_LICENCE.licence_interactions[0],
    )

    root = ET.fromstring(xml_request)

    assert root.find("ns:CommonSections/ns:returnURL", namespaces).text == "some return url"
    assert root.find("ns:CommonSections/ns:Branding/ns:logoUri", namespaces).text == authority_with_image.encoded_image
    assert root.find("ns:CommonSections/ns:Branding/ns:altText", namespaces).text == authority_with_image.name
    assert root.find("ns:CommonSections/ns:Branding/ns:colour", namespaces).text == "FFFFFF"
    assert (
        root.find("ns:CommonSections/ns:Branding/ns:HelpContact/ns:emailAddress", namespaces).text
        == TEST_DEPARTMENT.helpline_email_address
    )
    assert (
        root.find("ns:CommonSections/ns:Branding/ns:HelpContact/ns:telephone", namespaces).text
        == TEST_DEPARTMENT.helpline_phone_number
    )
    assert root.find("ns:CommonSections/ns:FormMetaData/ns:transactionId", namespaces).text == "Not Currently In Use"
    assert (
        root.find("ns:CommonSections/ns:FormMetaData/ns:formId", namespaces).text
        == TEST_LICENCE.licence_interactions[0].form.form_ref_number
    )
    assert (
        root.find("ns:CommonSections/ns:FormMetaData/ns:formName", namespaces).text
        == TEST_LICENCE.licence_interactions[0].licence_interaction_name
    )
    assert root.find("ns:CommonSections/ns:FormMetaData/ns:formalityId", namespaces).text == TEST_LICENCE.licence_code
    assert root.find("ns:CommonSections/ns:FormMetaData/ns:formalityVersion", namespaces).text == str(
        TEST_LICENCE.licence_interactions[0].form.form_version
    )
    assert (
        root.find("ns:CommonSections/ns:FormMetaData/ns:authorityShortName", namespaces).text
    ) == authority_with_image.name
    assert (
        root.find("ns:CommonSections/ns:FormMetaData/ns:authorityOrgName", namespaces).text
    ) == authority_with_image.full_name
    assert (
        root.find("ns:CommonSections/ns:FormMetaData/ns:governingLegislation", namespaces).text
        == TEST_CUSTOMISATION_FIXED_FEE.legislation_name
    )
    assert root.find("ns:CommonSections/ns:PaymentDetails/ns:isFixedFee", namespaces).text == "1"
    assert (
        root.find("ns:CommonSections/ns:PaymentDetails/ns:Payment", namespaces).text
        == TEST_CUSTOMISATION_FIXED_FEE.fixed_fee_amount.format_to_string_in_pounds
    )
    assert len(root.findall("ns:CommonSections/ns:Declarations/ns:Declaration", namespaces)) == len(
        TEST_CUSTOMISATION_FIXED_FEE.declarations
    )
