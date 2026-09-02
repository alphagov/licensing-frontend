import pytest

from citizen_frontend.api.repository.authority_repository import AuthorityRepository


@pytest.fixture
def mock_authority_model_filter(mocker):
    mock_model = mocker.patch("citizen_frontend.api.repository.authority_repository.Authority.objects.filter")
    yield mock_model


def test_get_offering_authorities_by_licence_code_calls_database_with_correct_method_and_args(
    mock_authority_model_filter,
):
    repo = AuthorityRepository()
    repo.get_offering_authorities_by_licence_code(licence_code="1234-5-6")

    mock_authority_model_filter.assert_called_with(
        licence_details__licence_code="1234-5-6", licence_details__offered_by_authority=True
    )
