import pytest
from common.models.interaction_customisations import InteractionCustomisation

import citizen_frontend.api.repository.interaction_customisation_repository as interaction_customisation_repository


@pytest.fixture
def mock_authority_model_filter(mocker):
    mocker.patch(
        "citizen_frontend.api.repository.interaction_customisation_repository.InteractionCustomisations.objects.filter"
    )


def test_find_published_customisation_has_published_constraint(mocker):
    queryset_cls = InteractionCustomisation.objects.all().__class__
    spy = mocker.spy(queryset_cls, "filter")
    interaction_customisation_repository.find_published_customisation("test_slug", "test_licence_code", 1, 1)
    has_constraint = any(call.kwargs.get("published_customisation__isnull") is False for call in spy.call_args_list)
    assert has_constraint
