from citizen_frontend.services.licence_lookup_service import LicenceLookupService
from citizen_frontend.tests.conftest import BASE_URL, TEST_AUTHORITY, TEST_LICENCE


def test_get_base_licence_url_when_authority_uses_gov_uk():
    licence_lookup_service = LicenceLookupService()
    result = licence_lookup_service.get_base_licence_url(
        licence=TEST_LICENCE, authority=TEST_AUTHORITY, uses_gov_uk=True
    )
    assert result == f"{BASE_URL}/apply-for-a-licence/test-licence/test-authority"
