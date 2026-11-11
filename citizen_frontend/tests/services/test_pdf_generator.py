import pytest
from conftest import TEST_AUTHORITY, TEST_CUSTOMISATION_FIXED_FEE, TEST_LICENCE, TEST_LICENCE_INTERACTION
from django.urls import reverse

from citizen_frontend.services.pdf_generation.pdf_generator import PdfGenerator


@pytest.fixture
def mock_service(mocker):
    service = PdfGenerator()
    mocker.patch.object(service, "pdf_provider")
    mocker.patch.object(service, "department_repository")

    yield service


def test_pdf_generator_calls_correct_services_with_args(mock_service, mocker):
    mock_create_file_path = mocker.patch.object(mock_service, "create_download_file_path")
    mock_create_file_path.return_value = (
        f"{TEST_AUTHORITY.name.replace(' ', '_')}_"
        f"{TEST_LICENCE_INTERACTION.licence_interaction_name.replace(' ', '_')}.pdf"
    )

    pdf_response = ""
    mock_service.pdf_provider.request_pdf_form.return_value = pdf_response

    expected = (
        pdf_response,
        (
            f"{TEST_AUTHORITY.name.replace(' ', '_')}_"
            f"{TEST_LICENCE_INTERACTION.licence_interaction_name.replace(' ', '_')}.pdf"
        ),
    )

    actual = mock_service.handle_request(
        authority=TEST_AUTHORITY,
        licence=TEST_LICENCE,
        interaction=TEST_LICENCE_INTERACTION,
        customisation=TEST_CUSTOMISATION_FIXED_FEE,
    )

    mock_service.department_repository.get_by_id.assert_called_with(
        department_id=(TEST_CUSTOMISATION_FIXED_FEE.department)
    )

    mock_service.pdf_provider.request_pdf_form.assert_called_with(
        authority=TEST_AUTHORITY,
        licence=TEST_LICENCE,
        department=mock_service.department_repository.get_by_id.return_value,
        customisation=TEST_CUSTOMISATION_FIXED_FEE,
        return_url=mock_service.create_return_url(
            licence_slug=TEST_LICENCE.url_slug,
            authority_slug=TEST_AUTHORITY.url_slug,
            interaction_id=TEST_LICENCE.licence_interactions[0].interaction_id,
            interaction_sub_id=TEST_LICENCE.licence_interactions[0].interaction_sub_id,
        ),
        interaction=TEST_LICENCE_INTERACTION,
    )

    mock_create_file_path.assert_called_with(authority=TEST_AUTHORITY, interaction=TEST_LICENCE_INTERACTION)

    assert actual == expected


def test_pdf_generator_creates_return_url(mock_service):

    expected_url = reverse(
        "begin_application_steps",
        kwargs={
            "licence_slug": TEST_LICENCE.url_slug,
            "authority_slug": TEST_AUTHORITY.url_slug,
            "interaction_id": TEST_LICENCE.licence_interactions[0].interaction_id,
            "interaction_sub_id": TEST_LICENCE.licence_interactions[0].interaction_sub_id,
        },
    )

    assert (
        mock_service.create_return_url(
            licence_slug=TEST_LICENCE.url_slug,
            authority_slug=TEST_AUTHORITY.url_slug,
            interaction_id=TEST_LICENCE.licence_interactions[0].interaction_id,
            interaction_sub_id=TEST_LICENCE.licence_interactions[0].interaction_sub_id,
        )
        == expected_url
    )


def test_pdf_generator_creates_download_file_path(mock_service):

    expected_download_file_path = (
        f"{TEST_AUTHORITY.name.replace(' ', '_')}_"
        f"{TEST_LICENCE_INTERACTION.licence_interaction_name.replace(' ', '_')}.pdf"
    )

    actual = mock_service.create_download_file_path(authority=TEST_AUTHORITY, interaction=TEST_LICENCE_INTERACTION)

    assert actual == expected_download_file_path


def test_handle_request_throws_error_no_department_found():
    pass
