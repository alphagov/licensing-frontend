from datetime import datetime, timedelta

import pytest
from common.models.licence_application import SupportingDocument
from common.models.shared_models import SupportingDocumentDefinition
from conftest import (
    TEST_AUTHORITY,
    TEST_CUSTOMISATION_NO_FEE,
    TEST_LICENCE,
    TEST_LICENCE_INTERACTION,
    TEST_UUID,
)
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError

VALID_LICENCE_APPLICATION_ARGS = {
    "email": "example@example.com",
    "application_document": SupportingDocument(
        id=f"{TEST_UUID}/file.pdf",
        file_name="file.pdf",
        definition=SupportingDocumentDefinition(
            name="Completed form",
            description="Downloaded and filled PDF form",
            is_mandatory=True,
        ),
    ),
    "supporting_documents": [],
    "authority": TEST_AUTHORITY,
    "licence": TEST_LICENCE,
    "customisation": TEST_CUSTOMISATION_NO_FEE,
    "interaction": TEST_LICENCE_INTERACTION,
    "is_supporting_documents_online": True,
}


def test_create_new_licence_application_calls_db_with_correct_args(mock_licence_application_repo):
    mock_licence_application_repo.model.full_clean.side_effect = None
    mock_licence_application_repo.counter_repo.get_next_count.return_value = 1

    actual = mock_licence_application_repo.create_new_licence_application(**VALID_LICENCE_APPLICATION_ARGS)

    mock_licence_application_repo.model.full_clean.assert_called()
    mock_licence_application_repo.model.save.assert_called()

    assert actual == f"{TEST_AUTHORITY.url_slug}-1"


def test_create_new_licence_application_calls_counter_repository_for_new_count(mock_licence_application_repo):
    mock_licence_application_repo.model.full_clean.side_effect = None

    mock_licence_application_repo.create_new_licence_application(**VALID_LICENCE_APPLICATION_ARGS)

    mock_licence_application_repo.counter_repo.get_next_count.assert_called()


def test_create_new_licence_application_handles_clean_errors(mock_licence_application_repo):
    mock_licence_application_repo.model.full_clean.side_effect = ValidationError("field: error")

    with pytest.raises(DataIntegrityError) as e:
        mock_licence_application_repo.create_new_licence_application(**VALID_LICENCE_APPLICATION_ARGS)

    assert e.value.args[0] == "LicenceApplication validation error: ['field: error'], failed to create new object"


def test_create_new_licence_application_handles_db_errors(mock_licence_application_repo):
    mock_licence_application_repo.model.save.side_effect = DatabaseError

    with pytest.raises(DocumentDBError) as e:
        mock_licence_application_repo.create_new_licence_application(**VALID_LICENCE_APPLICATION_ARGS)

    assert e.value.args[0] == "Failed to create new object, DB error: ()"


def test_calculate_expected_processing_date_only_working_days_false(mock_licence_application_repo):
    number_of_days_to_process = 20
    expected_processing_date = datetime.today() + timedelta(days=number_of_days_to_process)

    actual = mock_licence_application_repo.calculate_expected_processing_date(
        processing_days=number_of_days_to_process,
        is_working_days=False,
    )
    assert actual == expected_processing_date.date()
