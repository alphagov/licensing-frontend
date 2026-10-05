from copy import deepcopy

import pytest
from common.models.authorities import ContactDetails
from common.models.shared_models import PaymentAmount
from conftest import TEST_ISSUING_AUTHORITY
from pydantic import ValidationError

import citizen_frontend.services.licence_lookup_service as licence_lookup_service
from citizen_frontend.api.models.api_responses import (
    AuthorityContactDetails,
    AuthorityInteraction,
    LicenceAuthoritiesAndInteractionsResponse,
)
from citizen_frontend.enums.licence_interactions import LicenceInteractions
from citizen_frontend.enums.payment_type import PaymentType
from citizen_frontend.exceptions import DocumentDBError, LicenceLookupError
from citizen_frontend.services import authority_service
from citizen_frontend.tests.conftest import (
    BASE_URL,
    TEST_AUTHORITY,
    TEST_AUTHORITY_INTERACTION,
    TEST_CUSTOMISATION_FIXED_FEE,
    TEST_CUSTOMISATION_VARIABLE_FEE,
    TEST_LICENCE,
    TEST_LICENCE_CODE,
    TEST_SNAC_CODE,
)

TEST_AUTHORITY_INTERACTIONS_FOR_APPLY = {LicenceInteractions.APPLY.value: [TEST_AUTHORITY_INTERACTION]}


@pytest.fixture
def mock_get_licence_by_licence_code(mocker):
    yield mocker.patch.object(licence_lookup_service.licence_repository, "get_licence_by_licence_code")


@pytest.fixture
def mock_get_authorities_by_licence_code(mocker):
    yield mocker.patch.object(
        authority_service.authority_repository, "get_licence_offering_authorities_by_licence_code"
    )


@pytest.fixture
def mock_get_authority_licence_interaction_details(mocker):
    yield mocker.patch.object(licence_lookup_service, "get_authority_licence_interaction_details")


@pytest.fixture
def mock_check_if_location_specific(mocker):
    yield mocker.patch.object(licence_lookup_service, "check_if_location_specific")


@pytest.fixture
def mock_get_authorities(mocker):
    yield mocker.patch.object(licence_lookup_service, "get_authorities")


def test_get_licence_authorities_and_interactions_returns_none_when_no_licence_found(
    mock_get_licence_by_licence_code,
):
    mock_get_licence_by_licence_code.return_value = None

    result = licence_lookup_service.get_licence_authorities_and_interactions("unmatched-licence-code")

    assert result is None


# "Licence " + "unmatched-licence-code" + " doesn't exist"


def test_get_licence_authorities_and_interactions_returns_none_when_no_authorities_found_for_licence_without_snac(
    mock_get_licence_by_licence_code, mock_get_authorities_by_licence_code
):
    mock_get_licence_by_licence_code.return_value = TEST_LICENCE

    mock_get_authorities_by_licence_code.return_value = None

    result = licence_lookup_service.get_licence_authorities_and_interactions(TEST_LICENCE_CODE)

    assert result is None


# "No authorities found for the licence " + TEST_LICENCE_CODE)


def test_get_licence_authorities_and_interactions_returns_none_when_no_authorities_found_for_licence_with_snac(
    mock_get_licence_by_licence_code, mock_get_authorities_by_licence_code
):
    mock_get_licence_by_licence_code.return_value = TEST_LICENCE

    mock_get_authorities_by_licence_code.return_value = None

    result = licence_lookup_service.get_licence_authorities_and_interactions(TEST_LICENCE_CODE, TEST_SNAC_CODE)

    assert result is None


# "No authorities found for the licence " + TEST_LICENCE_CODE + " and for the SNAC/GSS Code " + TEST_SNAC_CODE


def test_get_licence_authorities_and_interactions_returns_expected_licence_authorities_and_interactions_response(
    mock_get_licence_by_licence_code,
    mock_get_authorities_by_licence_code,
    mock_get_authority_licence_interaction_details,
):
    mock_get_licence_by_licence_code.return_value = TEST_LICENCE
    mock_get_authorities_by_licence_code.return_value = [TEST_AUTHORITY]
    mock_get_authority_licence_interaction_details.return_value = TEST_ISSUING_AUTHORITY

    expected = LicenceAuthoritiesAndInteractionsResponse(
        is_location_specific=False,
        is_offered_by_county=TEST_LICENCE.is_offered_by_county,
        geographical_availability=TEST_LICENCE.administrative_area.countries,
        issuing_authorities=[TEST_ISSUING_AUTHORITY],
    )

    actual = licence_lookup_service.get_licence_authorities_and_interactions(TEST_LICENCE_CODE)

    assert actual == expected


def test_get_licence_authorities_and_interactions_when_given_multiple_authorities(
    mock_get_licence_by_licence_code,
    mock_get_authorities_by_licence_code,
    mock_get_authority_licence_interaction_details,
):
    contact_details_2 = ContactDetails(
        line_one="2 test authority",
        line_two="2 test road",
        line_three="",
        city="city",
        post_code="post2code",
        phone_number="0123456789",
        email="testauth2@email.com",
    )
    test_authority_2 = deepcopy(TEST_AUTHORITY)
    test_authority_2.full_name = "Test authority 2"
    test_authority_2.url_slug = "test-authority-2"
    test_authority_2.contact_details = contact_details_2
    test_authority_2_address_formatted = licence_lookup_service.format_postal_address(contact_details_2)

    test_issuing_authority_2 = deepcopy(TEST_ISSUING_AUTHORITY)
    test_issuing_authority_2.authority_name = test_authority_2.full_name
    test_issuing_authority_2.authority_slug = test_authority_2.url_slug
    test_issuing_authority_2.authority_contact = AuthorityContactDetails(
        website=test_authority_2.authority_url,
        email=test_authority_2.contact_details.email,
        phone=test_authority_2.contact_details.phone_number,
        address=test_authority_2_address_formatted,
    )

    mock_get_licence_by_licence_code.return_value = TEST_LICENCE
    mock_get_authorities_by_licence_code.return_value = [TEST_AUTHORITY, test_authority_2]
    mock_get_authority_licence_interaction_details.side_effect = [TEST_ISSUING_AUTHORITY, test_issuing_authority_2]

    expected = LicenceAuthoritiesAndInteractionsResponse(
        is_location_specific=False,
        is_offered_by_county=TEST_LICENCE.is_offered_by_county,
        geographical_availability=TEST_LICENCE.administrative_area.countries,
        issuing_authorities=[TEST_ISSUING_AUTHORITY, test_issuing_authority_2],
    )

    actual = licence_lookup_service.get_licence_authorities_and_interactions(TEST_LICENCE_CODE)

    assert actual == expected


def test_get_licence_authorities_and_interactions_when_location_specific_is_true_and_snac_code_not_present(
    mock_get_licence_by_licence_code,
    mock_get_authorities_by_licence_code,
    mock_get_authority_licence_interaction_details,
    mock_check_if_location_specific,
):
    mock_get_licence_by_licence_code.return_value = TEST_LICENCE
    mock_get_authorities_by_licence_code.return_value = [TEST_AUTHORITY]
    mock_get_authority_licence_interaction_details.return_value = TEST_ISSUING_AUTHORITY
    mock_check_if_location_specific.return_value = True

    licence_lookup_service.get_licence_authorities_and_interactions(TEST_LICENCE_CODE)

    mock_check_if_location_specific.assert_called()
    mock_get_authority_licence_interaction_details.assert_not_called()


def test_get_licence_authorities_and_interactions_when_location_specific_is_false_and_snac_code_not_present(
    mock_get_licence_by_licence_code,
    mock_get_authorities_by_licence_code,
    mock_get_authority_licence_interaction_details,
    mock_check_if_location_specific,
):
    mock_get_licence_by_licence_code.return_value = TEST_LICENCE
    mock_get_authorities_by_licence_code.return_value = [TEST_AUTHORITY]
    mock_get_authority_licence_interaction_details.return_value = TEST_ISSUING_AUTHORITY
    mock_check_if_location_specific.return_value = False

    licence_lookup_service.get_licence_authorities_and_interactions(TEST_LICENCE_CODE)

    mock_check_if_location_specific.assert_called()
    mock_get_authority_licence_interaction_details.assert_called_with(authority=TEST_AUTHORITY, licence=TEST_LICENCE)


def test_get_licence_authorities_and_interactions_when_location_specific_is_false_and_snac_code_present(
    mocker,
    mock_get_authority_licence_interaction_details,
    mock_check_if_location_specific,
    mock_get_licence_by_licence_code,
):
    mock_get_licence_by_licence_code.return_value = TEST_LICENCE
    mocker.patch.object(licence_lookup_service, "get_authorities", return_value=[TEST_AUTHORITY])
    mock_get_authority_licence_interaction_details.return_value = TEST_ISSUING_AUTHORITY
    mock_check_if_location_specific.return_value = False

    licence_lookup_service.get_licence_authorities_and_interactions(TEST_LICENCE_CODE, TEST_SNAC_CODE)

    mock_check_if_location_specific.assert_called()
    mock_get_authority_licence_interaction_details.assert_called_with(authority=TEST_AUTHORITY, licence=TEST_LICENCE)


def test_get_licence_authorities_and_interactions_when_location_specific_is_true_and_snac_code_present(
    mocker,
    mock_get_authority_licence_interaction_details,
    mock_check_if_location_specific,
    mock_get_licence_by_licence_code,
):
    mock_get_licence_by_licence_code.return_value = TEST_LICENCE
    mocker.patch.object(licence_lookup_service, "get_authorities", return_value=[TEST_AUTHORITY])
    mock_get_authority_licence_interaction_details.return_value = TEST_ISSUING_AUTHORITY
    mock_check_if_location_specific.return_value = True

    licence_lookup_service.get_licence_authorities_and_interactions(TEST_LICENCE_CODE, TEST_SNAC_CODE)

    mock_check_if_location_specific.assert_called()
    mock_get_authority_licence_interaction_details.assert_called_with(authority=TEST_AUTHORITY, licence=TEST_LICENCE)


def test_get_licence_url_when_authority_uses_gov_uk():
    result = licence_lookup_service.get_licence_url(
        licence_interaction=TEST_LICENCE.licence_interactions[0],
        licence=TEST_LICENCE,
        authority=TEST_AUTHORITY,
        uses_gov_uk=TEST_AUTHORITY.licence_details[0].using_gov_uk,
    )

    assert result == f"{BASE_URL}/apply-for-a-licence/test-licence/test-authority/apply-1"


def test_get_licence_url_when_authority_does_not_use_gov_uk():
    test_authority_not_using_gov_uk = deepcopy(TEST_AUTHORITY)
    test_authority_not_using_gov_uk.licence_details[0].using_gov_uk = False
    test_authority_not_using_gov_uk.licence_details[0].authority_url = "test-authority.gov.uk"

    result = licence_lookup_service.get_licence_url(
        licence_interaction=TEST_LICENCE.licence_interactions[0],
        licence=TEST_LICENCE,
        authority=test_authority_not_using_gov_uk,
        uses_gov_uk=test_authority_not_using_gov_uk.licence_details[0].using_gov_uk,
    )

    assert result == test_authority_not_using_gov_uk.licence_details[0].authority_url


def test_get_licence_url_returns_empty_string_when_no_matched_licence_details_found():
    test_authority_with_non_matching_licence_details = deepcopy(TEST_AUTHORITY)
    test_authority_with_non_matching_licence_details.licence_details[0].using_gov_uk = False
    test_authority_with_non_matching_licence_details.licence_details[0].authority_url = "test-authority.gov.uk"
    test_authority_with_non_matching_licence_details.licence_details[0].licence_code = "345-6-7"

    result = licence_lookup_service.get_licence_url(
        licence_interaction=TEST_LICENCE.licence_interactions[0],
        licence=TEST_LICENCE,
        authority=test_authority_with_non_matching_licence_details,
        uses_gov_uk=test_authority_with_non_matching_licence_details.licence_details[0].using_gov_uk,
    )

    assert result == ""


def test_get_licence_url_returns_empty_string_when_authority_url_is_empty():
    test_authority_with_empty_authority_url = deepcopy(TEST_AUTHORITY)
    test_authority_with_empty_authority_url.licence_details[0].using_gov_uk = False
    test_authority_with_empty_authority_url.licence_details[0].authority_url = ""

    result = licence_lookup_service.get_licence_url(
        licence_interaction=TEST_LICENCE.licence_interactions[0],
        licence=TEST_LICENCE,
        authority=test_authority_with_empty_authority_url,
        uses_gov_uk=test_authority_with_empty_authority_url.licence_details[0].using_gov_uk,
    )

    assert result == ""


def test_get_payment_info_from_customisation_returns_none_and_none_when_no_fee_required():
    customisation_no_fee_required = deepcopy(TEST_CUSTOMISATION_VARIABLE_FEE)
    customisation_no_fee_required.is_fee_required = False

    actual = licence_lookup_service.get_payment_info_from_customisation(customisation_no_fee_required)

    assert actual == (PaymentType.NONE, None)


def test_get_payment_info_from_customisation_returns_fixed_fee_and_amount_when_fixed_fee_required():
    actual = licence_lookup_service.get_payment_info_from_customisation(TEST_CUSTOMISATION_FIXED_FEE)

    assert actual == (PaymentType.FIXED_FEE, TEST_CUSTOMISATION_FIXED_FEE.fixed_fee_amount.format_to_string_in_pounds)


def test_get_payment_info_from_customisation_returns_variable_fee_and_none_when_fee_required_but_no_fixed_fee():
    actual = licence_lookup_service.get_payment_info_from_customisation(TEST_CUSTOMISATION_VARIABLE_FEE)

    assert actual == (PaymentType.VARIABLE_FEE, None)


def test_get_payment_info_from_customisation_returns_variable_fee_and_none_when_fee_required_and_fixed_fee_amount_0():
    customisation_fixed_fee_zero_pence = deepcopy(TEST_CUSTOMISATION_FIXED_FEE)
    customisation_fixed_fee_zero_pence.fixed_fee_amount = PaymentAmount(pence=0)

    actual = licence_lookup_service.get_payment_info_from_customisation(customisation_fixed_fee_zero_pence)

    assert actual == (PaymentType.VARIABLE_FEE, None)


def test_group_interactions(mocker):
    expected_grouped_interactions = {
        LicenceInteractions.APPLY.value: [TEST_LICENCE.licence_interactions[0], TEST_LICENCE.licence_interactions[1]],
        LicenceInteractions.RENEW.value: [TEST_LICENCE.licence_interactions[2]],
    }

    actual = licence_lookup_service.group_interactions(TEST_LICENCE)

    assert actual == expected_grouped_interactions


def test_build_authority_interactions(mocker):
    test_customisation = mocker.patch.object(
        licence_lookup_service.interaction_customisation_repository,
        "find_published_customisation",
        return_value=TEST_CUSTOMISATION_FIXED_FEE,
    )
    mock_group_interactions = mocker.patch.object(
        licence_lookup_service,
        "group_interactions",
        return_value={LicenceInteractions.APPLY.value: [TEST_LICENCE.licence_interactions[0]]},
    )

    expected = {
        LicenceInteractions.APPLY.value: [
            AuthorityInteraction(
                url="http://127.0.0.1:8000/apply-for-a-licence/test-licence/test-authority/apply-1",
                uses_licensify=True,
                uses_authority_url=False,
                description=mock_group_interactions.return_value["apply"][0].licence_interaction_name,
                payment=PaymentType.FIXED_FEE.value,
                payment_amount=test_customisation.return_value.fixed_fee_amount.format_to_string_in_pounds,
                introduction_text=test_customisation.return_value.introduction_text,
            )
        ]
    }

    actual = licence_lookup_service.build_authority_interactions(TEST_AUTHORITY, TEST_LICENCE)

    assert actual == expected


def test_get_authority_licence_interaction_details_returns_expected_issuing_authority(mocker):
    mocker.patch.object(
        licence_lookup_service, "build_authority_interactions", return_value=TEST_AUTHORITY_INTERACTIONS_FOR_APPLY
    )

    expected = TEST_ISSUING_AUTHORITY

    actual = licence_lookup_service.get_authority_licence_interaction_details(TEST_AUTHORITY, TEST_LICENCE)

    assert actual == expected


def test_get_licence_authorities_and_interactions_throws_error_licence_repository_error(
    mock_get_licence_by_licence_code,
):
    mock_get_licence_by_licence_code.side_effect = DocumentDBError("error message")

    with pytest.raises(LicenceLookupError) as e:
        licence_lookup_service.get_licence_authorities_and_interactions(TEST_AUTHORITY, TEST_LICENCE)

    assert e.value.args[0] == "error message"


def test_get_licence_authorities_and_interactions_throws_error_authority_repository_error(
    mock_get_licence_by_licence_code, mock_get_authorities
):
    mock_get_licence_by_licence_code.return_value = TEST_LICENCE
    mock_get_authorities.side_effect = DocumentDBError("error message")

    with pytest.raises(LicenceLookupError) as e:
        licence_lookup_service.get_licence_authorities_and_interactions(TEST_AUTHORITY, TEST_LICENCE)

    assert e.value.args[0] == "error message"


def test_get_licence_authorities_and_interactions_throws_error_interaction_customisation_repository_error(
    mock_get_licence_by_licence_code, mock_get_authorities, mock_find_interaction_customisation
):
    mock_get_licence_by_licence_code.return_value = TEST_LICENCE
    mock_get_authorities.return_value = [TEST_AUTHORITY]

    mock_find_interaction_customisation.side_effect = DocumentDBError("error message")

    with pytest.raises(LicenceLookupError) as e:
        licence_lookup_service.get_licence_authorities_and_interactions(TEST_AUTHORITY, TEST_LICENCE)

    assert e.value.args[0] == "error message"


def test_get_licence_authorities_and_interactions_throws_error_on_response_validation_error(
    mock_get_licence_by_licence_code, mock_get_authorities, mocker
):
    mock_get_licence_by_licence_code.return_value = TEST_LICENCE
    mock_get_authorities.return_value = [TEST_AUTHORITY]

    dummy_validation_error = ValidationError.from_exception_data(
        title="AuthorityInteraction",
        line_errors=[
            {
                "type": "string_type",
                "loc": ("url",),
                "msg": "Input should be a valid string",
                "input": 123,
            }
        ],
    )

    mocker.patch.object(licence_lookup_service, "build_authority_interactions", side_effect=dummy_validation_error)

    with pytest.raises(LicenceLookupError) as e:
        licence_lookup_service.get_licence_authorities_and_interactions(TEST_AUTHORITY, TEST_LICENCE)

    assert e.value.args[0] == "AuthorityInteraction validation error"
