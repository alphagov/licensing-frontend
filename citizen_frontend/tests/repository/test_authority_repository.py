import pytest
from conftest import TEST_AUTHORITY, TEST_LICENCE_CODE
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError
from citizen_frontend.repository.authority_repository import AuthorityRepository


@pytest.fixture
def repository(mocker):
    repo = AuthorityRepository()
    mocker.patch.object(repo.model.objects, "get")
    mocker.patch.object(repo.model.objects, "filter")
    yield repo


def test_get_offering_authorities_by_licence_code_calls_database_with_correct_method_and_args(repository):

    repository.get_licence_offering_authorities_by_licence_code(licence_code=TEST_LICENCE_CODE)

    repository.model.objects.filter.assert_called_with(
        licence_details__licence_code=TEST_LICENCE_CODE, licence_details__offered_by_authority=True
    )


def test_get_licence_offering_authorities_by_licence_code_throws_error_validation_error(mocker, repository):
    instance = TEST_AUTHORITY
    repository.model.objects.filter.return_value = [instance]

    mocker.patch.object(instance, "clean_fields", side_effect=[ValidationError("field error")])

    expected_error_message = "Authority validation error: ['field error']"

    with pytest.raises(DataIntegrityError) as e:
        repository.get_licence_offering_authorities_by_licence_code(licence_code=TEST_LICENCE_CODE)

    assert e.value.args[0] == expected_error_message


def test_get_licence_offering_authorities_by_licence_code_throws_error_database_error(repository):
    repository.model.objects.filter.side_effect = DatabaseError()
    expected_error_message = "There was a database error accessing Authorities collection"

    with pytest.raises(DocumentDBError) as e:
        repository.get_licence_offering_authorities_by_licence_code(licence_code=TEST_LICENCE_CODE)

    assert e.value.args[0] == expected_error_message


def test_find_authority_by_url_slug_calls_database_with_correct_method_and_args(repository):

    repository.find_authority_by_url_slug(TEST_AUTHORITY.url_slug)

    repository.model.objects.get.assert_called_with(
        url_slug=TEST_AUTHORITY.url_slug,
    )


def test_find_authority_by_url_slug_throws_error_on_clean_fields_failure(mocker, repository):
    instance = TEST_AUTHORITY
    repository.model.objects.get.return_value = instance

    mocker.patch.object(instance, "clean_fields", side_effect=[ValidationError("field error")])

    expected_error_message = "Authority validation error: ['field error']"

    with pytest.raises(DataIntegrityError) as e:
        repository.find_authority_by_url_slug(url_slug=TEST_AUTHORITY.url_slug)

    assert e.value.args[0] == expected_error_message


def test_find_authority_by_url_slug_throws_error_on_database_error(repository):
    repository.model.objects.get.side_effect = DatabaseError()

    expected_error_message = "There was a database error accessing Authorities collection"

    with pytest.raises(DocumentDBError) as e:
        repository.find_authority_by_url_slug(url_slug=TEST_AUTHORITY.url_slug)

    assert e.value.args[0] == expected_error_message
