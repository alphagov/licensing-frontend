import pytest
from conftest import TEST_LICENCE_CODE

from citizen_frontend.api.services.authority_service import AuthorityService


@pytest.fixture
def mock_service(mocker):
    service = AuthorityService()
    mocker.patch.object(service, "authority_repository")
    yield service


def test_get_authorities_for_licence_calls_authority_repository(mock_service):

    mock_service.get_authorities_for_licence(TEST_LICENCE_CODE)

    mock_service.authority_repository.get_licence_offering_authorities_by_licence_code.assert_called_with(
        licence_code=TEST_LICENCE_CODE
    )


def test_get_authorities_for_licence_with_locator():
    pass
