import pytest
from common.models.licence import Licence
from conftest import TEST_LICENCE
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError

import citizen_frontend.repository.licence_repository as licence_repository
from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError


@pytest.fixture
def mock_get_all(mocker):
    yield mocker.patch.object(Licence.objects, "all")


def test_get_licence_by_licence_code_calls_database_with_correct_method_and_args(mock_get_licence):
    licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    mock_get_licence.assert_called_with(licence_code=TEST_LICENCE.licence_code)


def test_get_licence_by_licence_code_returns_none_when_no_licence_matches(mock_get_licence):
    mock_get_licence.side_effect = Licence.DoesNotExist

    actual = licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert actual is None


def test_get_licence_by_licence_code_returns_expected_licence(mock_get_licence, mocker):
    mock_get_licence.return_value = TEST_LICENCE
    mocker.patch.object(TEST_LICENCE, "clean_fields")

    actual = licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    mock_get_licence.assert_called_with(licence_code=TEST_LICENCE.licence_code)
    assert actual == TEST_LICENCE


def test_get_licence_by_licence_code_throws_exception_clean_fields_error(mock_get_licence, mocker):
    instance = TEST_LICENCE

    mock_get_licence.return_value = instance

    mocker.patch.object(instance, "clean_fields", side_effect=ValidationError("field error message"))

    expected_error_message = "Licence validation error: field error message"

    with pytest.raises(DataIntegrityError) as e:
        licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert e.value.args[0] == expected_error_message


def test_get_licence_by_licence_code_throws_exception_more_than_one_licence_found(mock_get_licence):
    mock_get_licence.side_effect = Licence.MultipleObjectsReturned()

    expected_error_message = f"More than one licence found for licence code: {TEST_LICENCE.licence_code}"

    with pytest.raises(DataIntegrityError) as e:
        licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert e.value.args[0] == expected_error_message


def test_get_licence_by_licence_code_throws_exception_database_error(mock_get_licence):
    mock_get_licence.side_effect = DatabaseError()

    expected_error_message = f"DocumentDB error fetching licence: {TEST_LICENCE.licence_code}"

    with pytest.raises(DocumentDBError) as e:
        licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert e.value.args[0] == expected_error_message


def test_get_all_licences_from_database_throws_exception_validation_error(mocker, mock_get_all):
    mock_get_all.return_value = [TEST_LICENCE]

    mocker.patch.object(TEST_LICENCE, "clean_fields", side_effect=ValidationError("field error message"))

    expected_error_message = "Licence validation error: field error message"

    with pytest.raises(DataIntegrityError) as e:
        licence_repository.get_all_licences()
    assert e.value.args[0] == expected_error_message


def test_get_all_licences_from_database_throws_database_error(mock_get_all):
    mock_get_all.side_effect = DatabaseError()

    expected_error_message = "DocumentDB error fetching all licences"

    with pytest.raises(DocumentDBError) as e:
        licence_repository.get_all_licences()

    assert e.value.args[0] == expected_error_message


def test_get_all_licences_from_database_calls_database_with_correct_method(mock_get_all):
    licence_repository.get_all_licences()

    mock_get_all.assert_called_once()


def test_get_licence_by_url_slug_calls_database_with_correct_method_and_args(mock_get_licence):
    licence_repository.get_licence_by_url_slug(TEST_LICENCE.url_slug)

    mock_get_licence.assert_called_with(url_slug=TEST_LICENCE.url_slug)


def test_get_licence_by_url_slug_throws_error_on_clean_fields_failure(mock_get_licence, mocker):
    mock_get_licence.return_value = TEST_LICENCE

    mocker.patch.object(TEST_LICENCE, "clean_fields", side_effect=ValidationError("field error message"))

    expected_error_message = "Licence validation error: field error message"

    with pytest.raises(DataIntegrityError) as e:
        licence_repository.get_licence_by_url_slug(TEST_LICENCE.url_slug)
    assert e.value.args[0] == expected_error_message


def test_get_licence_by_url_slug_throws_error_on_database_error(mock_get_licence):
    mock_get_licence.side_effect = DatabaseError()

    expected_error_message = "DocumentDB error fetching licence"

    with pytest.raises(DocumentDBError) as e:
        licence_repository.get_licence_by_url_slug(TEST_LICENCE.url_slug)

    assert e.value.args[0] == expected_error_message


def test_get_licence_by_url_slug_throws_error_when_licence_does_not_exist(mock_get_licence):
    mock_get_licence.side_effect = Licence.DoesNotExist()

    expected_error_message = f"Licence does not exist: {TEST_LICENCE.url_slug}"

    with pytest.raises(ObjectDoesNotExist) as e:
        licence_repository.get_licence_by_url_slug(TEST_LICENCE.url_slug)

    assert e.value.args[0] == expected_error_message
