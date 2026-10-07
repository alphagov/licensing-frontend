import re

import pytest
from common.models.authorities import Authority, LicenceDetails
from conftest import TEST_AUTHORITY, TEST_LICENCE_CODE
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from citizen_frontend.api.repository.authority_repository import (
    find_licence_detail,
    get_licence_offering_authorities_by_licence_code,
)
from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError


@pytest.fixture
def mock_authority_model_filter(mocker):
    mock_filter = mocker.patch("citizen_frontend.api.repository.authority_repository.Authority.objects.filter")
    yield mock_filter


@pytest.fixture
def make_license_details():
    def _factory(codes=None):
        return [LicenceDetails(licence_code=code) for code in codes]

    return _factory


def test_get_offering_authorities_by_licence_code_calls_database_with_correct_method_and_args(
    mock_authority_model_filter,
):

    get_licence_offering_authorities_by_licence_code(licence_code=TEST_LICENCE_CODE)

    mock_authority_model_filter.assert_called_with(
        licence_details__licence_code=TEST_LICENCE_CODE, licence_details__offered_by_authority=True
    )


def test_find_licence_detail_finds_licence_with_matching_code(make_license_details):
    expected_licence_code = "5151-5-1"
    authority = Authority(licence_details=make_license_details(["1234-2-1", expected_licence_code, "3421-3-1"]))
    licence_detail = find_licence_detail(authority, expected_licence_code)
    assert licence_detail.licence_code == expected_licence_code


def test_find_licence_detail_throws_error_when_multiple_licences_found(make_license_details):
    expected_licence_code = "5151-5-1"
    authority = Authority(
        licence_details=make_license_details(["1234-2-1", expected_licence_code, expected_licence_code])
    )
    expected_error_message = re.compile(r"multiple matching", re.IGNORECASE)
    with pytest.raises(RuntimeError, match=expected_error_message):
        find_licence_detail(authority, expected_licence_code)


def test_find_licence_detail_returns_none_when_no_licence_with_matching_code(make_license_details):
    non_existing_licence_code = "5151-5-1"
    authority = Authority(licence_details=make_license_details(["1234-2-1", "2323-5-1", "3421-3-1"]))
    licence_detail = find_licence_detail(authority, non_existing_licence_code)
    assert licence_detail is None


def test_find_licence_detail_returns_none_when_empty_list():
    non_existing_licence_code = "5151-5-1"
    authority = Authority(licence_details=[])
    licence_detail = find_licence_detail(authority, non_existing_licence_code)
    assert licence_detail is None


def test_get_licence_offering_authorities_by_licence_code_throws_error_validation_error(
    mock_authority_model_filter, mocker
):
    instance = TEST_AUTHORITY
    mock_authority_model_filter.return_value = [instance]

    mocker.patch.object(instance, "full_clean", side_effect=[ValidationError("field error")])

    expected_error_message = "Authority validation error: field error"

    with pytest.raises(DataIntegrityError) as e:
        get_licence_offering_authorities_by_licence_code(licence_code=TEST_LICENCE_CODE)

    assert e.value.args[0] == expected_error_message


def test_get_licence_offering_authorities_by_licence_code_throws_error_database_error(
    mock_authority_model_filter,
):
    mock_authority_model_filter.side_effect = DatabaseError()
    expected_error_message = "There was a database error accessing Authorities collection"

    with pytest.raises(DocumentDBError) as e:
        get_licence_offering_authorities_by_licence_code(licence_code=TEST_LICENCE_CODE)

    assert e.value.args[0] == expected_error_message
