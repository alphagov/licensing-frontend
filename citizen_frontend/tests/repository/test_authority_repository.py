import pytest
from common.models.authority import Authority
from conftest import TEST_AUTHORITY, TEST_LICENCE_CODE
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError
from citizen_frontend.repository.authority_repository import (
    find_authority_by_url_slug,
    get_licence_offering_authorities_by_licence_code,
)


@pytest.fixture
def mock_authority_model_filter(mocker):
    yield mocker.patch.object(Authority.objects, "filter")


@pytest.fixture
def mock_authority_model_get(mocker):
    yield mocker.patch.object(Authority.objects, "get")


def test_get_offering_authorities_by_licence_code_calls_database_with_correct_method_and_args(
    mock_authority_model_filter,
):

    get_licence_offering_authorities_by_licence_code(licence_code=TEST_LICENCE_CODE)

    mock_authority_model_filter.assert_called_with(
        licence_details__licence_code=TEST_LICENCE_CODE, licence_details__offered_by_authority=True
    )


def test_get_licence_offering_authorities_by_licence_code_throws_error_validation_error(
    mock_authority_model_filter, mocker
):
    instance = TEST_AUTHORITY
    mock_authority_model_filter.return_value = [instance]

    mocker.patch.object(instance, "clean_fields", side_effect=[ValidationError("field error")])

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


def test_find_authority_by_url_slug_calls_database_with_correct_method_and_args(
    mock_authority_model_get,
):

    find_authority_by_url_slug(TEST_AUTHORITY.url_slug)

    mock_authority_model_get.assert_called_with(
        url_slug=TEST_AUTHORITY.url_slug,
    )


def test_find_authority_by_url_slug_throws_error_on_clean_fields_failure(mock_authority_model_get, mocker):
    instance = TEST_AUTHORITY
    mock_authority_model_get.return_value = instance

    mocker.patch.object(instance, "clean_fields", side_effect=[ValidationError("field error")])

    expected_error_message = "Authority validation error: field error"

    with pytest.raises(DataIntegrityError) as e:
        find_authority_by_url_slug(url_slug=TEST_AUTHORITY.url_slug)

    assert e.value.args[0] == expected_error_message


def test_find_authority_by_url_slug_throws_error_on_database_error(mock_authority_model_get):
    mock_authority_model_get.side_effect = DatabaseError()

    expected_error_message = "There was a database error accessing Authorities collection"

    with pytest.raises(DocumentDBError) as e:
        find_authority_by_url_slug(url_slug=TEST_AUTHORITY.url_slug)

    assert e.value.args[0] == expected_error_message
