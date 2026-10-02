import pytest
from common.models.licences import Licence
from conftest import TEST_LICENCE
from django.core.exceptions import ValidationError

import citizen_frontend.api.repository.licence_repository as licence_repository


def test_get_licence_by_licence_code_returns_none_when_no_licence_matches(mock_licence_filter):
    mock_licence_filter.side_effect = Licence.DoesNotExist

    actual = licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)
    mock_licence_filter.assert_called_with(licence_code=TEST_LICENCE.licence_code)

    assert actual is None


def test_get_licence_by_licence_code_throws_exception_full_clean_error(mock_licence_filter):
    mock_licence_filter.side_effect = ValidationError(message="field error message")

    with pytest.raises(ValidationError):
        licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)
