from io import BytesIO

import pytest
from conftest import TEST_AUTHORITY, TEST_LICENCE
from django.http import FileResponse
from django.urls import reverse

from citizen_frontend.exceptions import PDFGenerationGeneralError


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
    mocked_class = mocker.patch("citizen_frontend.views.PdfGenerator")
    service = mocked_class.return_value
    yield service


def test_generate_form_returns_file_response(client, generate_form_url, mock_pdf_generator):
    with open("citizen_frontend/services/resources/test_forms/fish_dealers_licence.pdf", "rb") as file:
        buffer = BytesIO(file.read())
        buffer.seek(0)

    mock_pdf_generator.handle_request.return_value = (buffer, "file_name")

    response = client.get(generate_form_url())

    assert type(response) is FileResponse
    assert response.status_code == 200


def test_generate_form_returns_500_response_general_pdf_generation_error(client, generate_form_url, mock_pdf_generator):
    mock_pdf_generator.handle_request.side_effect = PDFGenerationGeneralError("Error generating PDF")

    response = client.get(generate_form_url())

    assert response.status_code == 500
