import pytest
from conftest import TEST_AUTHORITY, TEST_LICENCE, TEST_LICENCE_INTERACTION
from django.urls import reverse

from citizen_frontend.services.pdf_generation.pdf_generator import PdfGenerator


@pytest.fixture
def mock_service(mocker):
    service = PdfGenerator()
    mocker.patch.object(service, "pdf_provider")
    mocker.patch.object(service, "licence_lookup_service")
    mocker.patch.object(service, "department_repository")

    yield service


def test_pdf_generator_calls_correct_services_with_args(mock_service, mocker):
    mock_create_file_path = mocker.patch.object(mock_service, "create_download_file_path")
    mock_create_file_path.return_value = (
        f"{TEST_AUTHORITY.name.replace(' ', '_')}_"
        f"{TEST_LICENCE_INTERACTION.licence_interaction_name.replace(' ', '_')}.pdf"
    )

    mock_service.licence_lookup_service.get_licence_interaction_context.return_value = (
        TEST_LICENCE,
        TEST_AUTHORITY,
        TEST_LICENCE_INTERACTION,
        None,
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
        authority_slug=TEST_AUTHORITY.url_slug,
        licence_slug=TEST_LICENCE.url_slug,
        licence_code=TEST_LICENCE.licence_code,
        interaction_id=TEST_LICENCE.licence_interactions[0].interaction_id,
        interaction_sub_id=TEST_LICENCE.licence_interactions[0].interaction_sub_id,
    )

    mock_service.licence_lookup_service.get_licence_interaction_context.assert_called_with(
        authority_url_slug=TEST_AUTHORITY.url_slug,
        licence_url_slug=TEST_LICENCE.url_slug,
        interaction=TEST_LICENCE.licence_interactions[0].interaction_id,
        interaction_sub_id=TEST_LICENCE.licence_interactions[0].interaction_sub_id,
    )

    (
        mock_service.licence_lookup_service.interaction_customisation_repository.find_published_customisation.assert_called_with(
            authority_url_slug=TEST_AUTHORITY.url_slug,
            licence_code=TEST_LICENCE.licence_code,
            interaction_id=TEST_LICENCE.licence_interactions[0].interaction_id,
            interaction_sub_id=TEST_LICENCE.licence_interactions[0].interaction_sub_id,
        )
    )

    mock_service.department_repository.get_by_id.assert_called_with(
        department_id=(
            mock_service.licence_lookup_service.interaction_customisation_repository.find_published_customisation.return_value.department
        )
    )

    mock_service.pdf_provider.request_pdf_form.assert_called_with(
        authority=mock_service.licence_lookup_service.get_licence_interaction_context.return_value[1],
        licence=mock_service.licence_lookup_service.get_licence_interaction_context.return_value[0],
        department=mock_service.department_repository.get_by_id.return_value,
        customisation=(
            mock_service.licence_lookup_service.interaction_customisation_repository.find_published_customisation.return_value
        ),
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
