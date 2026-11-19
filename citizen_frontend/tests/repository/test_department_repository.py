import pytest
from conftest import TEST_DEPARTMENT
from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError
from citizen_frontend.repository.department_repository import DepartmentRepository


@pytest.fixture
def mock_repository(mocker):
    repo = DepartmentRepository()
    mocker.patch.object(repo.model.objects, "get")
    return repo


def test_get_department_from_authority_slug_calls_database_with_correct_method_and_args(mock_repository):
    mock_repository.get_department_from_authority_slug("authority-slug")

    mock_repository.model.objects.get.assert_called()


def test_get_department_from_authority_slug_throws_validation_error(mock_repository, mocker):
    instance = TEST_DEPARTMENT
    mock_repository.model.objects.get.return_value = instance

    mocker.patch.object(instance, "clean_fields", side_effect=ValidationError("field error"))

    with pytest.raises(DataIntegrityError):
        mock_repository.get_department_from_authority_slug("authority-slug")


def test_get_department_from_authority_slug_throws_database_error(mock_repository, mocker):
    mock_repository.model.objects.get.side_effect = DatabaseError()

    with pytest.raises(DocumentDBError) as e:
        mock_repository.get_department_from_authority_slug("authority-slug")
