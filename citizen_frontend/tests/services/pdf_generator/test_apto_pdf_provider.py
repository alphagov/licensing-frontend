import os
import xml.etree.ElementTree as ET
from copy import deepcopy
from io import BytesIO

import pytest
from conftest import (
    TEST_AUTHORITY,
    TEST_CUSTOMISATION_FIXED_FEE,
    TEST_CUSTOMISATION_VARIABLE_FEE,
    TEST_DEPARTMENT,
    TEST_LICENCE,
)

from citizen_frontend.exceptions import PDFProviderUnavailableError
from citizen_frontend.services.pdf_generation.pdf_provider import APTOPdfProvider, AptoStatuses


@pytest.fixture
def apto_pdf_provider():
    yield APTOPdfProvider()


namespaces = {
    "ns": "http://www.aptosolutions.co.uk/businesslink/psc/common/2.3",
    "common": "http://www.aptosolutions.co.uk/businesslink/psc/common/2.3",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}


def test_request_pdf_happy_path(apto_pdf_provider):
    pass


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
    free_customisation = deepcopy(TEST_CUSTOMISATION_FIXED_FEE)
    free_customisation.is_fee_required = False

    xml_request = apto_pdf_provider.create_xml_request(
        licence=TEST_LICENCE,
        authority=TEST_AUTHORITY,
        customisation=free_customisation,
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


def test_apto_pdf_provider_checks_apto_availability_on_pdf_generation(apto_pdf_provider, mocker):
    status_check = mocker.patch.object(apto_pdf_provider, "get_apto_pdf_status_setting")
    apto_pdf_provider.request_pdf_form(
        authority=TEST_AUTHORITY,
        licence=TEST_LICENCE,
        department=TEST_DEPARTMENT,
        customisation=TEST_CUSTOMISATION_FIXED_FEE,
        interaction=TEST_LICENCE.licence_interactions[0],
        return_url="",
    )
    status_check.assert_called()


def test_apto_pdf_provider_throws_error_apto_not_available(apto_pdf_provider, mocker):
    mocker.patch.object(apto_pdf_provider, "get_apto_pdf_status_setting", return_value=False)

    with pytest.raises(PDFProviderUnavailableError):
        apto_pdf_provider.request_pdf_form(
            authority=TEST_AUTHORITY,
            licence=TEST_LICENCE,
            department=TEST_DEPARTMENT,
            customisation=TEST_CUSTOMISATION_FIXED_FEE,
            interaction=TEST_LICENCE.licence_interactions[0],
            return_url="",
        )


def test_apto_pdf_provider_sends_post_request_to_apto_with_correct_body(apto_pdf_provider, mocker):
    mocker.patch.object(apto_pdf_provider, "get_apto_pdf_status_setting", return_value=True)
    mock_post = mocker.patch("citizen_frontend.services.pdf_generation.pdf_provider.requests.post")

    expected_xml_body = apto_pdf_provider.create_xml_request(
        authority=TEST_AUTHORITY,
        licence=TEST_LICENCE,
        customisation=TEST_CUSTOMISATION_FIXED_FEE,
        interaction=TEST_LICENCE.licence_interactions[0],
        return_url="",
        department=TEST_DEPARTMENT,
    ).encode("utf-8")

    stream = BytesIO(expected_xml_body)

    mocker.patch("citizen_frontend.services.pdf_generation.pdf_provider.BytesIO", return_value=stream)

    apto_pdf_provider.request_pdf_form(
        authority=TEST_AUTHORITY,
        licence=TEST_LICENCE,
        department=TEST_DEPARTMENT,
        customisation=TEST_CUSTOMISATION_FIXED_FEE,
        interaction=TEST_LICENCE.licence_interactions[0],
        return_url="",
    )

    mock_post.assert_called_with(
        url=f"{os.getenv('APTO_REQUEST_BASE_URL')}/Licence/{TEST_LICENCE.licence_interactions[0].form.form_ref_number}",
        files={
            "AttachedData": ("customisationFile.xml", stream, "text/xml"),
        },
    )


def test_apto_pdf_provider_throws_error_on_non_200_response_from_apto_request():
    pass


def test_apto_not_found():
    # TODO frontend/app/uk/gov/gds/licensing/frontend/controllers/FormProxyController.scala
    #  Render not found page, should happen in the controller layer but currently the form proxy does this
    #  and the PDF generator throws this, custom errors?
    pass


def test_apto_not_published():
    # TODO frontend/app/uk/gov/gds/licensing/frontend/controllers/FormProxyController.scala
    #   Render contact page, should happen in the view controller layer,
    #   PDF generator throws this too
    pass


def test_get_apto_pdf_status_setting_calls_settings_repo_with_correct_args(apto_pdf_provider, mocker):
    settings_repo = mocker.patch.object(apto_pdf_provider, "settings_repo")

    apto_pdf_provider.get_apto_pdf_status_setting()

    settings_repo.get_setting.assert_called_with(key="aptoStatus")


def test_get_apto_pdf_status_setting_returns_false_apto_unavailable(apto_pdf_provider, mocker):
    mocker.patch.object(apto_pdf_provider, "settings_repo", return_value=AptoStatuses.NOT_AVAILABLE)

    actual = apto_pdf_provider.get_apto_pdf_status_setting()

    assert not actual
