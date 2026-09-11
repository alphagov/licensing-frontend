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

interaction_customisation_with_unset_published_customisation = InteractionCustomisation(
    interaction_id=TEST_INTERACTION_ID,
    interaction_sub_id=int(TEST_INTERACTION_SUB_ID_INT),
    licence_code=TEST_LICENCE_CODE,
    authority_url_slug=TEST_AUTH_SLUG,
)

interaction_customisation_with_published_customisation = deepcopy(
    interaction_customisation_with_unset_published_customisation
)
interaction_customisation_with_published_customisation.published_customisation = TEST_CUSTOMISATION_FIXED_FEE

interaction_customisations_with_published_customisation_of_none = deepcopy(
    interaction_customisation_with_published_customisation
)
interaction_customisations_with_published_customisation_of_none.published_customisation = None


def test_get_offering_authorities_by_licence_code_calls_database_with_correct_method_and_args(
    mock_interaction_customisation_filter,
):
    interaction_customisation_repository.find_interaction_customisation(
        TEST_AUTH_SLUG, TEST_LICENCE_CODE, TEST_INTERACTION_ID, TEST_INTERACTION_SUB_ID_INT
    )
    mock_interaction_customisation_filter.assert_called_with(
        authority_url_slug=TEST_AUTH_SLUG,
        licence_code=TEST_LICENCE_CODE,
        interaction_id=TEST_INTERACTION_ID,
        interaction_sub_id=TEST_INTERACTION_SUB_ID_INT,
    )


def test_find_published_customisation_correctly_returns_published_customisation(mock_find_interaction_customisation):
    mock_find_interaction_customisation.return_value = interaction_customisation_with_published_customisation

    customisation = interaction_customisation_repository.find_published_customisation(
        TEST_AUTH_SLUG, TEST_LICENCE_CODE, TEST_INTERACTION_ID, TEST_INTERACTION_SUB_ID_INT
    )
    assert customisation == TEST_CUSTOMISATION_FIXED_FEE


def test_find_published_customisation_returns_none_when_interaction_customisation_has_no_published_customisation(
    mock_find_interaction_customisation,
):
    mock_find_interaction_customisation.return_value = interaction_customisation_with_unset_published_customisation
    customisation = interaction_customisation_repository.find_published_customisation(
        TEST_AUTH_SLUG, TEST_LICENCE_CODE, TEST_INTERACTION_ID, TEST_INTERACTION_SUB_ID_INT
    )
    assert customisation is None


def test_find_published_customisation_returns_none_when_interaction_customisation_not_found(
    mock_find_interaction_customisation,
):
    mock_find_interaction_customisation.return_value = None
    customisation = interaction_customisation_repository.find_published_customisation(
        TEST_AUTH_SLUG, TEST_LICENCE_CODE, TEST_INTERACTION_ID, TEST_INTERACTION_SUB_ID_INT
    )
    assert customisation is None


def test_find_published_customisation_returns_none_when_interaction_customisation_has_published_customisation_of_none(
    mock_find_interaction_customisation,
):
    mock_find_interaction_customisation.return_value = interaction_customisations_with_published_customisation_of_none
    customisation = interaction_customisation_repository.find_published_customisation(
        TEST_AUTH_SLUG, TEST_LICENCE_CODE, TEST_INTERACTION_ID, TEST_INTERACTION_SUB_ID_INT
    )
    assert customisation is None


def test_find_published_customisation_doesnt_return_suspended_published_customisation(
    mock_find_interaction_customisation,
):
    interaction_customisation_with_suspended_customisation = deepcopy(
        interaction_customisation_with_published_customisation
    )
    interaction_customisation_with_suspended_customisation.published_customisation.suspended_at = datetime.now()
    mock_find_interaction_customisation.return_value = interaction_customisation_with_suspended_customisation
    customisation = interaction_customisation_repository.find_published_customisation(
        TEST_AUTH_SLUG, TEST_LICENCE_CODE, TEST_INTERACTION_ID, TEST_INTERACTION_SUB_ID_INT
    )
    assert customisation is None
