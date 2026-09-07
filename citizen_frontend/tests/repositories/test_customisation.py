import pytest

from citizen_frontend.repositories.interaction_customisation import InteractionCustomisationRepository


@pytest.fixture
def mock_authority_model_filter(mocker):
    mock_model = mocker.patch(
        "citizen_frontend.api.repository.interaction_customisation_repository.InteractionCustomisations.objects.filter"
    )
    yield mock_model


def test_find_published_customisation_has_published_constraint(mock_authority_model_filter):
    InteractionCustomisationRepository.find_published_interaction_customisation("test_slug", "test_liceence_code", 1, 1)
