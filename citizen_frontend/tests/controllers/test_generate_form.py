import pytest
from bson import ObjectId
from common.models.department import Department
from conftest import TEST_AUTHORITY, TEST_CUSTOMISATION_FIXED_FEE, TEST_LICENCE
from django.http import FileResponse
from django.urls import reverse

from citizen_frontend.services import licence_lookup_service
from citizen_frontend.services.pdf_provider import APTOPdfProvider


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
def mock_get_licence_interaction_context(mocker):
    yield mocker.patch.object(licence_lookup_service, "get_licence_interaction_context")


@pytest.fixture
def mock_apto_pdf_provider(mocker):
    mocker.patch("citizen_frontend.services.pdf_provider.APTOPdfProvider.generate_pdf")
    instance = APTOPdfProvider()
    yield instance


def test_generate_form_returns_file_response(
    client,
    generate_form_url,
    mock_authority_repository,
    mock_licence_repository,
    mock_get_licence_interaction_context,
    mocker,
):
    mock_get_licence_interaction_context.return_value = (
        TEST_AUTHORITY,
        TEST_LICENCE,
        TEST_CUSTOMISATION_FIXED_FEE,
        None,
    )

    mocker.patch.object(
        licence_lookup_service.interaction_customisation_repository,
        "find_published_customisation",
        return_value=TEST_CUSTOMISATION_FIXED_FEE,
    )

    mock_get = mocker.patch.object(Department.objects, "get")
    mock_get.return_value = Department(_id=ObjectId("50c8520393867870cb0d775f"), authority_slug=TEST_AUTHORITY.url_slug)

    response = client.get(generate_form_url())

    assert type(response) is FileResponse
    assert response.status_code == 200


def test_generate_form_calls_licence_lookup_service_for_context(
    client, generate_form_url, mock_get_licence_interaction_context, mocker
):
    mock_get_licence_interaction_context.return_value = (
        TEST_AUTHORITY,
        TEST_LICENCE,
        TEST_CUSTOMISATION_FIXED_FEE,
        None,
    )
    mocker.patch.object(Department.objects, "get")

    mocker.patch.object(
        licence_lookup_service.interaction_customisation_repository,
        "find_published_customisation",
        return_value=TEST_CUSTOMISATION_FIXED_FEE,
    )

    client.get(generate_form_url())

    mock_get_licence_interaction_context.assert_called_with(
        authority_url_slug=TEST_AUTHORITY.url_slug,
        licence_url_slug=TEST_LICENCE.url_slug,
        interaction=TEST_LICENCE.licence_interactions[0].interaction_id,
        interaction_sub_id=TEST_LICENCE.licence_interactions[0].interaction_sub_id,
    )


def test_generate_form_gets_published_customisation(
    client, generate_form_url, mock_get_licence_interaction_context, mocker
):

    mock_get_licence_interaction_context.return_value = (
        TEST_AUTHORITY,
        TEST_LICENCE,
        TEST_CUSTOMISATION_FIXED_FEE,
        None,
    )

    test_customisation = mocker.patch.object(
        licence_lookup_service.interaction_customisation_repository,
        "find_published_customisation",
        return_value=TEST_CUSTOMISATION_FIXED_FEE,
    )
    mocker.patch.object(Department.objects, "get")

    client.get(generate_form_url())

    test_customisation.assert_called_with(
        authority_url_slug=TEST_AUTHORITY.url_slug,
        licence_code=TEST_LICENCE.licence_code,
        interaction_id=TEST_LICENCE.licence_interactions[0].interaction_id,
        interaction_sub_id=TEST_LICENCE.licence_interactions[0].interaction_sub_id,
    )


def test_generate_form_gets_department(client, generate_form_url, mock_get_licence_interaction_context, mocker):
    mock_get_licence_interaction_context.return_value = (
        TEST_AUTHORITY,
        TEST_LICENCE,
        TEST_CUSTOMISATION_FIXED_FEE,
        None,
    )

    mocker.patch.object(
        licence_lookup_service.interaction_customisation_repository,
        "find_published_customisation",
        return_value=TEST_CUSTOMISATION_FIXED_FEE,
    )

    mock_get = mocker.patch.object(Department.objects, "get")
    mock_get.return_value = Department(_id=ObjectId("50c8520393867870cb0d775f"), authority_slug=TEST_AUTHORITY.url_slug)

    client.get(generate_form_url())
    mock_get.assert_called()


def test_generate_form_uses_pdf_provider(
    client, generate_form_url, mocker, mock_get_licence_interaction_context, mock_apto_pdf_provider
):
    mock_get_licence_interaction_context.return_value = (
        TEST_AUTHORITY,
        TEST_LICENCE,
        TEST_CUSTOMISATION_FIXED_FEE,
        None,
    )

    mocker.patch.object(
        licence_lookup_service.interaction_customisation_repository,
        "find_published_customisation",
        return_value=TEST_CUSTOMISATION_FIXED_FEE,
    )

    mock_get = mocker.patch.object(Department.objects, "get")
    mock_get.return_value = Department(_id=ObjectId("50c8520393867870cb0d775f"), authority_slug=TEST_AUTHORITY.url_slug)

    client.get(generate_form_url())

    mock_apto_pdf_provider.generate_pdf.assert_called()
