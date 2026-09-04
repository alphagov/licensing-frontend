from copy import deepcopy

from citizen_frontend.services.licence_lookup_service import LicenceLookupService
from citizen_frontend.tests.conftest import BASE_URL, TEST_AUTHORITY, TEST_LICENCE


def test_get_base_licence_url_when_authority_uses_gov_uk():
    licence_lookup_service = LicenceLookupService()
    result = licence_lookup_service.get_base_licence_url(
        licence=TEST_LICENCE, authority=TEST_AUTHORITY, uses_gov_uk=True
    )
    assert result == f"{BASE_URL}/apply-for-a-licence/test-licence/test-authority"


def test_get_base_licence_url_when_authority_does_not_use_gov_uk():
    test_authority_not_using_gov_uk = deepcopy(TEST_AUTHORITY)
    test_authority_not_using_gov_uk.licence_details[0].using_gov_uk = False
    test_authority_not_using_gov_uk.licence_details[0].authority_url = "test-authority.gov.uk"
    licence_lookup_service = LicenceLookupService()
    result = licence_lookup_service.get_base_licence_url(
        licence=TEST_LICENCE, authority=TEST_AUTHORITY, uses_gov_uk=False
    )
    assert result == test_authority_not_using_gov_uk.licence_details[0].authority_url
