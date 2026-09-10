from copy import deepcopy

from common.models.interaction_customisations import InteractionCustomisation
from conftest import TEST_AUTH_SLUG, TEST_INTERACTION_ID, TEST_INTERACTION_SUB_ID, TEST_LICENCE_CODE

from citizen_frontend.api.repository.interaction_customisation_repository import find_interaction_customisations


def test_get_offering_authorities_by_licence_code_calls_database_with_correct_method_and_args(
    mock_interaction_customisation_filter,
):
    find_interaction_customisations("test-slug", "test-code", 5, 6)
    mock_interaction_customisation_filter.assert_called_with(
        authority_url_slug="test-slug",
        licence_code="test-code",
        interaction_id=5,
        interaction_sub_id=6,
    )


def test_find_published_customisation_correctly_returns_published_customisation(mock_find_interaction_customisations):
    matching_interaction_customisation = InteractionCustomisation(
        interaction_id=TEST_INTERACTION_ID,
        interaction_sub_id=int(TEST_INTERACTION_SUB_ID),
        licence_code=TEST_LICENCE_CODE,
        authority_url_slug=TEST_AUTH_SLUG,
    )
    unmatching_interaction_customisation = deepcopy(matching_interaction_customisation)

