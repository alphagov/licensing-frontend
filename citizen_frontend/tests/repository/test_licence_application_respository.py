from datetime import datetime

import pytest
from common.models.licence_application import SupportingDocument
from common.models.shared_models import SupportingDocumentDefinition
from conftest import (
    TEST_AUTHORITY,
    TEST_CUSTOMISATION_NO_FEE,
    TEST_LICENCE,
    TEST_UUID,
)
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import DatabaseError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError
from citizen_frontend.services.application_submission_service import Application

MOCK_PDF_CONTENT = b"%PDF-1.4 fake pdf content"

MOCK_EXPECTED_PROCESSING_DATE = datetime.fromisoformat("2026-12-01")

VALID_FORM_SUBMISSION = {
    "email": "anemail@example.com",
    "confirmation_email": "anemail@example.com",
    "application_upload": SimpleUploadedFile(
        name="application_upload.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
    ),
    "supporting_document_0": SimpleUploadedFile(
        name="supporting_document_0.pdf", content_type="application/pdf", content=MOCK_PDF_CONTENT
    ),
    "declaration": "on",
}

VALID_LICENCE_APPLICATION_ARGS = {
    "application_submission": Application(
        email=VALID_FORM_SUBMISSION["email"],
        files={
            "application_upload": VALID_FORM_SUBMISSION["application_upload"],
            "supporting_document_0": VALID_FORM_SUBMISSION["supporting_document_0"],
        },
        licence=TEST_LICENCE,
        authority=TEST_AUTHORITY,
        customisation=TEST_CUSTOMISATION_NO_FEE,
        interaction=TEST_LICENCE.licence_interactions[0],
        are_supporting_documents_online=False,
    ),
    "supporting_documents": [],
    "application_document": SupportingDocument(
        id=f"{TEST_UUID}/file.pdf",
        file_name="file.pdf",
        definition=SupportingDocumentDefinition(
            name="Completed form",
            description="Downloaded and filled PDF form",
            is_mandatory=True,
        ),
    ),
    "expected_processing_date": MOCK_EXPECTED_PROCESSING_DATE,
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
