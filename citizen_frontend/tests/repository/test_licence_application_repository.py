import pytest
from conftest import TEST_LICENCE_APPLICATION
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError
from citizen_frontend.repository.licence_application_repository import LicenceApplicationRepository


@pytest.fixture
def mock_repository(mocker):
    repo = LicenceApplicationRepository()
    mocker.patch.object(repo.model.objects, "get")
    return repo


def test_get_application_from_id_calls_database_with_correct_method_and_args(mock_repository):
    mock_repository.get_application_from_id("ApplicationRef1")

    mock_repository.model.objects.get.assert_called()


def test_get_application_from_id_throws_validation_error(mock_repository, mocker):
    instance = TEST_LICENCE_APPLICATION
    mock_repository.model.objects.get.return_value = instance

    mocker.patch.object(instance, "clean_fields", side_effect=[ValidationError("field error")])

    with pytest.raises(DataIntegrityError):
        mock_repository.get_application_from_id("ApplicationRef1")


def test_get_application_from_id_throws_database_error(mock_repository, mocker):
    mock_repository.model.objects.get.side_effect = DatabaseError()

    with pytest.raises(DocumentDBError):
        mock_repository.get_application_from_id("ApplicationRef1")
