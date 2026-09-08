import pytest
from common.models.interaction_customisations import InteractionCustomisation

import citizen_frontend.repositories.interaction_customisation as interaction_customisation_repository


@pytest.fixture
def mock_authority_model_filter(mocker):
    mocker.patch(
        "citizen_frontend.api.repository.interaction_customisation_repository.InteractionCustomisations.objects.filter"
    )


def test_find_published_customisation_has_published_constraint(mocker):
    spy = mocker.spy(InteractionCustomisation.objects, "filter")
    interaction_customisation_repository.find_published_interaction_customisation(
        "test_slug", "test_licence_code", 1, 1
    )
    print(spy.call_args.kwargs)
    assert spy.call_args.kwargs.get("published_customisation__isnull") is False
