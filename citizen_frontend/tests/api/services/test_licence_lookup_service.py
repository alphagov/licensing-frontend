from copy import deepcopy

import pytest
from common.models.shared_models import PaymentAmount

import citizen_frontend.services.licence_lookup_service as licence_lookup_service
from citizen_frontend.api.models.api_responses import AuthorityInteraction, LicenceAuthoritiesAndInteractionsResponse
from citizen_frontend.enums.licence_interactions import LicenceInteractions
from citizen_frontend.enums.payment_type import PaymentType
from citizen_frontend.services import authority_service
from citizen_frontend.tests.conftest import (
    BASE_URL,
    TEST_AUTHORITY,
    TEST_CUSTOMISATION_FIXED_FEE,
    TEST_CUSTOMISATION_VARIABLE_FEE,
    TEST_LICENCE,
    TEST_LICENCE_CODE,
    TEST_SNAC_CODE,
)


@pytest.fixture
def mock_get_licence_by_licence_code(mocker):
    yield mocker.patch.object(licence_lookup_service.licence_repository, "get_licence_by_licence_code")


@pytest.fixture
def mock_get_authorities_by_licence_code(mocker):
    yield mocker.patch.object(
        authority_service.authority_repository, "get_licence_offering_authorities_by_licence_code"
    )


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


def test_get_licence_authorities_and_interactions_calls_licence_repository(mock_get_licence_by_licence_code):
    mock_get_licence_by_licence_code.return_value = None

    licence_lookup_service.get_licence_authorities_and_interactions("unmatched-licence-code")

    mock_get_licence_by_licence_code.assert_called_with("unmatched-licence-code")


def test_get_licence_authorities_and_interactions_returns_string_when_no_licence_found(
    mock_get_licence_by_licence_code,
):
    mock_get_licence_by_licence_code.return_value = None

    result = licence_lookup_service.get_licence_authorities_and_interactions("unmatched-licence-code")

    assert result == "Licence " + "unmatched-licence-code" + " doesn't exist"


def test_get_licence_authorities_and_interactions_returns_string_when_no_authorities_found_for_licence_without_snac(
    mock_get_licence_by_licence_code, mock_get_authorities_by_licence_code
):
    mock_get_licence_by_licence_code.return_value = TEST_LICENCE

    mock_get_authorities_by_licence_code.return_value = None

    result = licence_lookup_service.get_licence_authorities_and_interactions(TEST_LICENCE_CODE)

    assert result == "No authorities found for the licence " + TEST_LICENCE_CODE


def test_get_licence_authorities_and_interactions_returns_string_when_no_authorities_found_for_licence_with_snac(
    mock_get_licence_by_licence_code, mock_get_authorities_by_licence_code
):
    mock_get_licence_by_licence_code.return_value = TEST_LICENCE

    mock_get_authorities_by_licence_code.return_value = None

    result = licence_lookup_service.get_licence_authorities_and_interactions(TEST_LICENCE_CODE, TEST_SNAC_CODE)

    assert (
        result
        == "No authorities found for the licence " + TEST_LICENCE_CODE + " and for the SNAC/GSS Code " + TEST_SNAC_CODE
    )


def test_get_licence_authorities_and_interactions_returns_licence_authorities_and_interactions_response(
    mock_get_licence_by_licence_code, mock_get_authorities_by_licence_code
):
    mock_get_licence_by_licence_code.return_value = TEST_LICENCE

    mock_get_authorities_by_licence_code.return_value = [TEST_AUTHORITY]

    result = licence_lookup_service.get_licence_authorities_and_interactions(TEST_LICENCE_CODE)

    assert isinstance(result, LicenceAuthoritiesAndInteractionsResponse)


def test_group_interactions(mocker):
    result = licence_lookup_service.group_interactions(TEST_LICENCE)

    assert result.keys() == {LicenceInteractions.APPLY, LicenceInteractions.RENEW}
    assert len(result[LicenceInteractions.APPLY]) == 2
    assert len(result[LicenceInteractions.RENEW]) == 1


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


# def test_get_authority_licence_interaction_details_returns_issuing_authority_object(mocker):
#     mocker.patch.object(
#         licence_lookup_service.licence_repository, "get_licence_by_licence_code", return_value=TEST_LICENCE
#     )
#     mocker.patch.object(
#         authority_service.authority_repository,
#         "get_licence_offering_authorities_by_licence_code",
#         return_value=[TEST_AUTHORITY],
#     )
#     mocker.patch.object(
#         licence_lookup_service, "get_authority_licence_interaction_details", return_value=[TEST_AUTHORITY_INTERACTION]
#     )
#
#     result = licence_lookup_service.get_licence_authorities_and_interactions(TEST_LICENCE_CODE)
#
#     assert isinstance(result.issuing_authorities[0], IssuingAuthority)
