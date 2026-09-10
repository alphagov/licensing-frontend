from copy import deepcopy
from datetime import datetime

from common.models.interaction_customisations import InteractionCustomisation
from conftest import (
    TEST_AUTH_SLUG,
    TEST_CUSTOMISATION_FIXED_FEE,
    TEST_INTERACTION_ID,
    TEST_INTERACTION_SUB_ID_INT,
    TEST_LICENCE_CODE,
)

import citizen_frontend.api.repository.interaction_customisation_repository as interaction_customisation_repository

base_interaction_customisation = InteractionCustomisation(
    interaction_id=TEST_INTERACTION_ID,
    interaction_sub_id=int(TEST_INTERACTION_SUB_ID_INT),
    licence_code=TEST_LICENCE_CODE,
    authority_url_slug=TEST_AUTH_SLUG,
)

matching_interaction_customisation = deepcopy(base_interaction_customisation)
matching_interaction_customisation.published_customisation = TEST_CUSTOMISATION_FIXED_FEE

unmatching_interaction_customisation = deepcopy(matching_interaction_customisation)
unmatching_interaction_customisation.published_customisation = None


def test_get_offering_authorities_by_licence_code_calls_database_with_correct_method_and_args(
    mock_interaction_customisation_filter,
):
    interaction_customisation_repository.find_interaction_customisations(
        TEST_AUTH_SLUG, TEST_LICENCE_CODE, TEST_INTERACTION_ID, TEST_INTERACTION_SUB_ID_INT
    )
    mock_interaction_customisation_filter.assert_called_with(
        authority_url_slug=TEST_AUTH_SLUG,
        licence_code=TEST_LICENCE_CODE,
        interaction_id=TEST_INTERACTION_ID,
        interaction_sub_id=TEST_INTERACTION_SUB_ID_INT,
    )


def test_find_published_customisation_correctly_returns_published_customisation(mock_find_interaction_customisations):
    mock_find_interaction_customisations.return_value = [
        unmatching_interaction_customisation,
        matching_interaction_customisation,
    ]
    customisation = interaction_customisation_repository.find_published_customisation(
        TEST_AUTH_SLUG, TEST_LICENCE_CODE, TEST_INTERACTION_ID, TEST_INTERACTION_SUB_ID_INT
    )
    assert len(customisation) == 1
    assert customisation[0] == TEST_CUSTOMISATION_FIXED_FEE


def test_find_published_customisation_returns_empty_list_when_no_interaction_customisations_has_published_customisation(
    mock_find_interaction_customisations,
):
    mock_find_interaction_customisations.return_value = [
        unmatching_interaction_customisation,
        base_interaction_customisation,
    ]
    customisation = interaction_customisation_repository.find_published_customisation(
        TEST_AUTH_SLUG, TEST_LICENCE_CODE, TEST_INTERACTION_ID, TEST_INTERACTION_SUB_ID_INT
    )
    assert len(customisation) == 0


def test_find_published_customisation_doesnt_return_suspended_published_customisation(
    mock_find_interaction_customisations,
):
    interaction_customisation_with_suspended_customisation = deepcopy(matching_interaction_customisation)
    interaction_customisation_with_suspended_customisation.published_customisation.suspended_at = datetime.now()
    mock_find_interaction_customisations.return_value = [interaction_customisation_with_suspended_customisation]
    customisation = interaction_customisation_repository.find_published_customisation(
        TEST_AUTH_SLUG, TEST_LICENCE_CODE, TEST_INTERACTION_ID, TEST_INTERACTION_SUB_ID_INT
    )
    assert len(customisation) == 0
