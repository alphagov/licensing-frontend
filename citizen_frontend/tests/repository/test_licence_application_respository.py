from common.models.licence_application import SupportingDocument
from common.models.shared_models import SupportingDocumentDefinition
from conftest import TEST_AUTHORITY, TEST_CUSTOMISATION_NO_FEE, TEST_LICENCE, TEST_LICENCE_INTERACTION, TEST_UUID


def test_create_new_licence_application_calls_db_with_correct_args(mock_licence_application_repo, mock_bson_object_id):
    mock_licence_application_repo.model.full_clean.side_effect = None

    actual = mock_licence_application_repo.create_new_licence_application(
        email="example@example.com",
        application_document=SupportingDocument(
            _id=f"{TEST_UUID}/file.pdf",
            file_name="file.pdf",
            definition=SupportingDocumentDefinition(
                name="Completed form",
                description="Downloaded and filled PDF form",
                is_mandatory=True,
            ),
        ),
        supporting_documents=[],
        authority=TEST_AUTHORITY,
        licence=TEST_LICENCE,
        customisation=TEST_CUSTOMISATION_NO_FEE,
        interaction=TEST_LICENCE_INTERACTION,
        is_supporting_documents_online=True,
    )

    mock_licence_application_repo.model.full_clean.assert_called()
    mock_licence_application_repo.model.save.assert_called()

    assert actual == mock_bson_object_id
