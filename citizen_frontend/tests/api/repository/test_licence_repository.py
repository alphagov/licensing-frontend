import pytest
from common.models.licences import Licence
from conftest import TEST_LICENCE
from django.core.exceptions import ValidationError
from django.db import DatabaseError

import citizen_frontend.api.repository.licence_repository as licence_repository
from citizen_frontend.exceptions import LicenceDataError, LicenceDBError


def test_get_licence_by_licence_code_returns_none_when_no_licence_matches(mock_get_licence):
    mock_get_licence.side_effect = Licence.DoesNotExist

    actual = licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)
    mock_get_licence.assert_called_with(licence_code=TEST_LICENCE.licence_code)

    assert actual is None


def test_get_licence_by_licence_code_throws_exception_full_clean_error(mock_get_licence):
    mock_get_licence.side_effect = ValidationError(message="field error message")

    expected_error_message = "Licence validation error: field error message"

    with pytest.raises(LicenceDataError) as e:
        licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert e.value.args[0] == expected_error_message


def test_get_licence_by_licence_code_throws_exception_more_than_one_licence_found(mock_get_licence):
    mock_get_licence.side_effect = Licence.MultipleObjectsReturned()

    expected_error_message = f"More than one licence found for licence code: {TEST_LICENCE.licence_code}"

    with pytest.raises(LicenceDataError) as e:
        licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert e.value.args[0] == expected_error_message


def test_get_licence_by_licence_code_throws_exception_database_error(mock_get_licence):
    mock_get_licence.side_effect = DatabaseError()

    expected_error_message = f"DocumentDB error fetching licence: {TEST_LICENCE.licence_code}"

    with pytest.raises(LicenceDBError) as e:
        licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert e.value.args[0] == expected_error_message
