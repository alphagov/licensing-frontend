import pytest
from common.models.licence import Licence, LicenceInteraction

from citizen_frontend.exceptions import DataIntegrityError
from citizen_frontend.services.licence_service import LicenceService


@pytest.fixture
def service():
    return LicenceService()


def make_licence_interactions(interactions: tuple(int, int)) -> list[LicenceInteraction]:

    return [
        LicenceInteraction(interaction_id=interaction_id, interaction_sub_id=interaction_sub_id)
        for interaction_id, interaction_sub_id in interactions
    ]


def test_find_interaction_finds_interaction_only_when_both_ids_match(service):
    expected_interaction_id = 15
    expected_sub_interaction_id = 2
    licence = Licence(
        licence_interactions=make_licence_interactions(
            [
                (expected_interaction_id, 1),
                (expected_interaction_id, expected_sub_interaction_id),
                (12, expected_sub_interaction_id),
            ]
        )
    )
    interaction = service.find_interaction(licence, expected_interaction_id, expected_sub_interaction_id)
    assert interaction.interaction_id == expected_interaction_id
    assert interaction.interaction_sub_id == expected_sub_interaction_id


def test_find_interaction_throws_error_when_multiple_interactions_found(service):
    expected_interaction_id = 15
    expected_sub_interaction_id = 2
    licence = Licence(
        licence_interactions=make_licence_interactions(
            [
                (expected_interaction_id, expected_sub_interaction_id),
                (expected_interaction_id, expected_sub_interaction_id),
                (12, 1),
            ]
        )
    )
    expected_error_message = "Multiple matching interactions found"
    with pytest.raises(DataIntegrityError) as e:
        service.find_interaction(licence, expected_interaction_id, expected_sub_interaction_id)
    assert e.value.args[0] == expected_error_message


def test_find_interaction_returns_none_when_no_licence_with_matching_code(service):
    not_expected_interaction_id = 15
    not_expected_sub_interaction_id = 2
    licence = Licence(
        licence_interactions=make_licence_interactions(
            [(not_expected_interaction_id, 1), (11, not_expected_sub_interaction_id), (12, 1)]
        )
    )
    interaction = service.find_interaction(licence, not_expected_interaction_id, not_expected_sub_interaction_id)
    assert interaction is None


def test_find_interaction_returns_none_when_empty_list(service):
    not_expected_interaction_id = 15
    not_expected_sub_interaction_id = 2
    licence = Licence(licence_interactions=[])
    interaction = service.find_interaction(licence, not_expected_interaction_id, not_expected_sub_interaction_id)
    assert interaction is None
