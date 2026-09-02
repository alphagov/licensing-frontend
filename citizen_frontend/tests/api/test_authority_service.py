import pytest

from citizen_frontend.api.services.authority_service import AuthorityService


@pytest.fixture
def mock_service(mocker):
    service = AuthorityService()
    mocker.patch.object(service, "authority_repository")
    yield service


def test_get_authorities_for_licence_calls_authority_repository(mock_service):

    mock_service.get_authorities_for_licence()

    mock_service.authority_repository.get_offering_authorities_by_licence_code.assert_called()


def test_get_authorities_for_licence_with_locator():
    pass
