from copy import deepcopy

from common.models.shared_models import PaymentAmount
from conftest import TEST_CUSTOMISATION_FIXED_FEE, TEST_CUSTOMISATION_VARIABLE_FEE

import citizen_frontend.services.licence_lookup_service as licence_lookup_service
from citizen_frontend.enums.licence_interactions import LicenceInteractions
from citizen_frontend.enums.payment_type import PaymentType
from citizen_frontend.tests.conftest import BASE_URL, TEST_AUTHORITY, TEST_LICENCE


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

    assert actual == (PaymentType.FIXED_FEE, TEST_CUSTOMISATION_FIXED_FEE.fixed_fee_amount)


def test_get_payment_info_from_customisation_returns_variable_fee_and_none_when_fee_required_but_no_fixed_fee():
    actual = licence_lookup_service.get_payment_info_from_customisation(TEST_CUSTOMISATION_VARIABLE_FEE)

    assert actual == (PaymentType.VARIABLE_FEE, None)


def test_get_payment_info_from_customisation_returns_variable_fee_and_none_when_fee_required_and_fixed_fee_amount_0():
    customisation_fixed_fee_zero_pence = deepcopy(TEST_CUSTOMISATION_FIXED_FEE)
    customisation_fixed_fee_zero_pence.fixed_fee_amount = PaymentAmount(pence=0)

    actual = licence_lookup_service.get_payment_info_from_customisation(customisation_fixed_fee_zero_pence)

    assert actual == (PaymentType.VARIABLE_FEE, None)


def test_get_licence_interaction_context_returns_none_when_no_licence_found(
    mock_licence_repository, mock_authority_repository
):
    mock_licence_repository.get_licence_by_url_slug.return_value = None
    actual = licence_lookup_service.get_licence_interaction_context(
        "authority", "url_slug", str(LicenceInteractions.RENEW), 5
    )
    assert actual is None


def test_get_licence_interaction_context_returns_none_when_no_authority_found(
    mock_licence_repository, mock_authority_repository
):
    mock_authority_repository.find_authority_by_url_slug.return_value = None
    actual = licence_lookup_service.get_licence_interaction_context(
        "authority", "url_slug", str(LicenceInteractions.RENEW), 5
    )
    assert actual is None


def test_get_licence_interaction_context_returns_none_when_no_licence_interaction_found(
    mock_licence_repository, mock_authority_repository, mocker
):
    mock_licence = mocker.MagicMock()
    mock_licence.find_interaction.return_value = None
    mock_licence_repository.get_licence_by_url_slug.return_value = mock_licence
    actual = licence_lookup_service.get_licence_interaction_context(
        "authority", "url_slug", str(LicenceInteractions.RENEW), 5
    )
    assert actual is None


def test_get_licence_interaction_context_returns_none_when_no_licence_details_found(
    mock_licence_repository, mock_authority_repository, mocker
):
    mock_authority = mocker.MagicMock()
    mock_authority.find_licence_detail.return_value = None
    mock_authority_repository.find_authority_by_url_slug.return_value = mock_authority
    actual = licence_lookup_service.get_licence_interaction_context(
        "authority", "url_slug", str(LicenceInteractions.RENEW), 5
    )
    assert actual is None


def test_get_licence_interaction_context_returns_all_data_when_all_data_found(
    mock_licence_repository, mock_authority_repository, mocker
):
    mock_authority = mocker.MagicMock()
    mock_authority.url_slug = "url_slug"

    mock_licence = mocker.MagicMock()
    mock_licence.licence_code = "licence_code"

    mock_authority_repository.find_authority_by_url_slug.return_value = mock_authority
    mock_licence_repository.get_licence_by_url_slug.return_value = mock_licence
    actual = licence_lookup_service.get_licence_interaction_context(
        "authority", "url_slug", str(LicenceInteractions.RENEW), 5
    )
    assert actual is not None
    assert actual.authority.url_slug == "url_slug"
    assert actual.licence.licence_code == "licence_code"
    assert actual.interaction is not None
    assert actual.licence_detail is not None
