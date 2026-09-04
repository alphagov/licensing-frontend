from copy import deepcopy

from citizen_frontend.services.licence_lookup_service import LicenceLookupService
from citizen_frontend.tests.conftest import BASE_URL, TEST_AUTHORITY, TEST_LICENCE


def test_get_licence_url_when_authority_uses_gov_uk():
    licence_lookup_service = LicenceLookupService()
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
    licence_lookup_service = LicenceLookupService()

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
    licence_lookup_service = LicenceLookupService()

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
    licence_lookup_service = LicenceLookupService()

    result = licence_lookup_service.get_licence_url(
        licence_interaction=TEST_LICENCE.licence_interactions[0],
        licence=TEST_LICENCE,
        authority=test_authority_with_empty_authority_url,
        uses_gov_uk=test_authority_with_empty_authority_url.licence_details[0].using_gov_uk,
    )

    assert result == ""
