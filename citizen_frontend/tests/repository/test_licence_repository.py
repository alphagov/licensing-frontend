import pytest
from common.models.licence import Licence
from conftest import TEST_LICENCE
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError
from citizen_frontend.repository.licence_repository import LicenceRepository


@pytest.fixture
def repository(mocker):
    repo = LicenceRepository()
    mocker.patch.object(repo.model.objects, "get")
    mocker.patch.object(repo.model.objects, "filter")
    mocker.patch.object(repo.model.objects, "all")
    return repo


def test_get_licence_by_licence_code_calls_database_with_correct_method_and_args(repository):
    repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    repository.model.objects.get.assert_called_with(licence_code=TEST_LICENCE.licence_code)


def test_get_licence_by_licence_code_returns_none_when_no_licence_matches(repository):
    repository.model.objects.get.side_effect = Licence.DoesNotExist

    actual = repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert actual is None


def test_get_licence_by_licence_code_returns_expected_licence(repository, mocker):
    repository.model.objects.get.return_value = TEST_LICENCE
    mocker.patch.object(TEST_LICENCE, "clean_fields")

    actual = repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    repository.model.objects.get.assert_called_with(licence_code=TEST_LICENCE.licence_code)
    assert actual == TEST_LICENCE


def test_get_licence_by_licence_code_throws_exception_clean_fields_error(repository, mocker):
    instance = TEST_LICENCE

    repository.model.objects.get.return_value = instance

    mocker.patch.object(instance, "clean_fields", side_effect=ValidationError("field error message"))

    expected_error_message = "Licence validation error: ['field error message']"

    with pytest.raises(DataIntegrityError) as e:
        repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert e.value.args[0] == expected_error_message


def test_get_licence_by_licence_code_throws_exception_more_than_one_licence_found(repository):
    repository.model.objects.get.side_effect = Licence.MultipleObjectsReturned()

    expected_error_message = f"More than one licence found for licence code: {TEST_LICENCE.licence_code}"

    with pytest.raises(DataIntegrityError) as e:
        repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert e.value.args[0] == expected_error_message


def test_get_licence_by_licence_code_throws_exception_database_error(repository):
    repository.model.objects.get.side_effect = DatabaseError()

    expected_error_message = f"DocumentDB error fetching licence: {TEST_LICENCE.licence_code}"

    with pytest.raises(DocumentDBError) as e:
        repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert e.value.args[0] == expected_error_message


def test_get_all_licences_from_database_throws_exception_validation_error(mocker, repository):
    repository.model.objects.all.return_value = [TEST_LICENCE]

    mocker.patch.object(TEST_LICENCE, "clean_fields", side_effect=ValidationError("field error message"))

    expected_error_message = "Licence validation error: ['field error message']"

    with pytest.raises(DataIntegrityError) as e:
        repository.get_all_licences()
    assert e.value.args[0] == expected_error_message


def test_get_all_licences_from_database_throws_database_error(repository):
    repository.model.objects.all.side_effect = DatabaseError()

    expected_error_message = "DocumentDB error fetching all licences"

    with pytest.raises(DocumentDBError) as e:
        repository.get_all_licences()

    assert e.value.args[0] == expected_error_message


def test_get_licence_by_url_slug_calls_database_with_correct_method_and_args(repository):
    repository.get_licence_by_url_slug(TEST_LICENCE.url_slug)

    repository.model.objects.get.assert_called_with(url_slug=TEST_LICENCE.url_slug)


def test_get_licence_by_url_slug_throws_error_on_clean_fields_failure(repository, mocker):
    repository.model.objects.get.return_value = TEST_LICENCE

    mocker.patch.object(TEST_LICENCE, "clean_fields", side_effect=ValidationError("field error message"))

    expected_error_message = "Licence validation error: ['field error message']"

    with pytest.raises(DataIntegrityError) as e:
        repository.get_licence_by_url_slug(TEST_LICENCE.url_slug)
    assert e.value.args[0] == expected_error_message


def test_get_licence_by_url_slug_throws_error_on_database_error(repository):
    repository.model.objects.get.side_effect = DatabaseError()

    expected_error_message = "DocumentDB error fetching licence"

    with pytest.raises(DocumentDBError) as e:
        repository.get_licence_by_url_slug(TEST_LICENCE.url_slug)

    assert e.value.args[0] == expected_error_message


def test_get_licence_by_url_slug_throws_error_when_licence_does_not_exist(repository):
    repository.model.objects.get.side_effect = Licence.DoesNotExist()

    expected_error_message = f"Licence does not exist: {TEST_LICENCE.url_slug}"

    with pytest.raises(ObjectDoesNotExist) as e:
        repository.get_licence_by_url_slug(TEST_LICENCE.url_slug)

    assert e.value.args[0] == expected_error_message
