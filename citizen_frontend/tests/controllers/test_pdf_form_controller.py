from io import BytesIO

import pytest
from conftest import TEST_AUTHORITY, TEST_LICENCE
from django.http import FileResponse
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

from citizen_frontend.exceptions import (
    LicenceLookupError,
    PDFGenerationGeneralError,
    PDFProviderUnavailableError,
)


@pytest.fixture
def generate_form_url():
    def _url(**overrides) -> str:
        defaults = {
            "licence_slug": TEST_LICENCE.url_slug,
            "authority_slug": TEST_AUTHORITY.url_slug,
            "licence_code": TEST_LICENCE.licence_code,
            "interaction_id": TEST_LICENCE.licence_interactions[0].interaction_id,
            "interaction_sub_id": TEST_LICENCE.licence_interactions[0].interaction_sub_id,
        }

        merged_kwargs = {**defaults, **overrides}
        return reverse("generate_form", kwargs=merged_kwargs)

    return _url


@pytest.fixture
def mock_pdf_generator(mocker):
    mocked_class = mocker.patch("citizen_frontend.controllers.pdf_form_controller.PdfGenerator")
    service = mocked_class.return_value
    yield service


def test_generate_pdf_form_happy_path(
    client,
    generate_form_url,
    mock_pdf_generator,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
):
    with open("citizen_frontend/services/resources/test_forms/fish_dealers_licence.pdf", "rb") as file:
        buffer = BytesIO(file.read())
        buffer.seek(0)

    mock_pdf_generator.handle_request.return_value = (buffer, "file_name")

    response = client.get(generate_form_url())

    mock_get_licence_interaction_context.assert_called_with(
        authority_url_slug=TEST_AUTHORITY.url_slug,
        licence_url_slug=TEST_LICENCE.url_slug,
        interaction=TEST_LICENCE.licence_interactions[0].interaction_id,
        interaction_sub_id=TEST_LICENCE.licence_interactions[0].interaction_sub_id,
    )

    mock_find_published_customisation_with_fixed_fee.assert_called_with(
        authority_url_slug=TEST_AUTHORITY.url_slug,
        licence_code=TEST_LICENCE.licence_code,
        interaction_id=TEST_LICENCE.licence_interactions[0].interaction_id,
        interaction_sub_id=TEST_LICENCE.licence_interactions[0].interaction_sub_id,
    )
    mock_pdf_generator.handle_request.assert_called_with(
        authority=mock_get_licence_interaction_context.return_value[1],
        licence=mock_get_licence_interaction_context.return_value[0],
        interaction=mock_get_licence_interaction_context.return_value[2],
        customisation=mock_find_published_customisation_with_fixed_fee.return_value,
    )
    assert type(response) is FileResponse
    assert response.status_code == 200


def test_generate_pdf_form_returns_500_response_general_pdf_generation_error(
    client,
    generate_form_url,
    mock_pdf_generator,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
):
    mock_pdf_generator.handle_request.side_effect = PDFGenerationGeneralError("Error generating PDF")

    response = client.get(generate_form_url())

    assert response.status_code == 500
    assertTemplateUsed(response, "citizen_frontend/error.html")


def test_generate_pdf_form_returns_503_response_pdf_unavailable_error(
    client,
    generate_form_url,
    mock_pdf_generator,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
):
    mock_pdf_generator.handle_request.side_effect = PDFProviderUnavailableError("Error generating PDF, unavailable")

    response = client.get(generate_form_url())

    assert response.status_code == 503
    assertTemplateUsed(response, "citizen_frontend/error.html")


def test_generate_pdf_form_renders_contact_details_form_not_published(
    client,
    generate_form_url,
    mock_get_licence_interaction_context,
    mock_find_published_customisation_with_fixed_fee,
):
    mock_find_published_customisation_with_fixed_fee.return_value = None
    response = client.get(generate_form_url())

    assert response.status_code == 200
    assertTemplateUsed(response, "citizen_frontend/licence_not_available_online_page.html")


def test_generate_pdf_form_renders_not_found_when_form_not_found_exception(client, generate_form_url, mocker):
    mock_lookup = mocker.patch("citizen_frontend.controllers.pdf_form_controller.licence_lookup_service")
    mock_lookup.get_licence_interaction_context.side_effect = LicenceLookupError("No licence found")

    response = client.get(generate_form_url())

    assert response.status_code == 404
    assertTemplateUsed(response, "404.html")
