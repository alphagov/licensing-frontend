import pytest
from conftest import TEST_LICENCE_CODE
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from citizen_frontend.api.repository.authority_repository import get_licence_offering_authorities_by_licence_code
from citizen_frontend.exceptions import AuthorityDataError, AuthorityDBError


@pytest.fixture
def mock_authority_model_filter(mocker):
    mock_model = mocker.patch("citizen_frontend.api.repository.authority_repository.Authority.objects.filter")
    yield mock_model


def test_get_offering_authorities_by_licence_code_calls_database_with_correct_method_and_args(
    mock_authority_model_filter,
):

    get_licence_offering_authorities_by_licence_code(licence_code=TEST_LICENCE_CODE)

    mock_authority_model_filter.assert_called_with(
        licence_details__licence_code=TEST_LICENCE_CODE, licence_details__offered_by_authority=True
    )


def test_get_licence_offering_authorities_by_licence_code_throws_error_validation_error(
    mock_authority_model_filter,
):
    mock_authority_model_filter.side_effect = ValidationError(message="field error")
    expected_error_message = "Authority validation error: field error"

    with pytest.raises(AuthorityDataError) as e:
        get_licence_offering_authorities_by_licence_code(licence_code=TEST_LICENCE_CODE)

    assert e.value.args[0] == expected_error_message


def test_get_licence_offering_authorities_by_licence_code_throws_error_database_error(
    mock_authority_model_filter,
):
    mock_authority_model_filter.side_effect = DatabaseError()
    expected_error_message = "There was a database error"

    with pytest.raises(AuthorityDBError) as e:
        get_licence_offering_authorities_by_licence_code(licence_code=TEST_LICENCE_CODE)

    assert e.value.args[0] == expected_error_message
