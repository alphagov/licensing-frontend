import re

import pytest
from common.models.licences import Licence, LicenceInteraction
from conftest import TEST_LICENCE
from django.core.exceptions import ValidationError
from django.db import DatabaseError

import citizen_frontend.api.repository.licence_repository as licence_repository
from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError


@pytest.fixture
def mock_get_all(mocker):
    yield mocker.patch.object(Licence.objects, "all")


def test_get_licence_by_licence_code_calls_database_with_correct_method_and_args(mock_get_licence):
    licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    mock_get_licence.assert_called_with(licence_code=TEST_LICENCE.licence_code)


@pytest.fixture
def make_licence_interactions():
    def _factory(interactions=None):
        return [
            LicenceInteraction(interaction_id=interaction_id, interaction_sub_id=interaction_sub_id)
            for interaction_id, interaction_sub_id in interactions
        ]

    return _factory


def test_find_licence_interaction_finds_interaction_only_when_both_ids_match(make_licence_interactions):
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
    interaction = licence_repository.find_interaction(licence, expected_interaction_id, expected_sub_interaction_id)
    assert interaction.interaction_id == expected_interaction_id
    assert interaction.interaction_sub_id == expected_sub_interaction_id


def test_find_licence_interaction_throws_error_when_multiple_licences_found(make_licence_interactions):
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
    expected_error_message = re.compile(r"multiple matching", re.IGNORECASE)
    with pytest.raises(RuntimeError, match=expected_error_message):
        licence_repository.find_interaction(licence, expected_interaction_id, expected_sub_interaction_id)


def test_find_licence_interaction_returns_none_when_no_licence_with_matching_code(make_licence_interactions):
    not_expected_interaction_id = 15
    not_expected_sub_interaction_id = 2
    licence = Licence(
        licence_interactions=make_licence_interactions(
            [(not_expected_interaction_id, 1), (11, not_expected_sub_interaction_id), (12, 1)]
        )
    )
    interaction = licence_repository.find_interaction(
        licence, not_expected_interaction_id, not_expected_sub_interaction_id
    )
    assert interaction is None


def test_find_licence_interaction_returns_none_when_empty_list():
    not_expected_interaction_id = 15
    not_expected_sub_interaction_id = 2
    licence = Licence(licence_interactions=[])
    interaction = licence_repository.find_interaction(
        licence, not_expected_interaction_id, not_expected_sub_interaction_id
    )
    assert interaction is None


def test_get_licence_by_licence_code_returns_none_when_no_licence_matches(mock_get_licence):
    mock_get_licence.side_effect = Licence.DoesNotExist

    actual = licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert actual is None


def test_get_licence_by_licence_code_returns_expected_licence(mock_get_licence, mocker):
    mock_get_licence.return_value = TEST_LICENCE
    mocker.patch.object(TEST_LICENCE, "full_clean")

    actual = licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    mock_get_licence.assert_called_with(licence_code=TEST_LICENCE.licence_code)
    assert actual == TEST_LICENCE


def test_get_licence_by_licence_code_throws_exception_full_clean_error(mock_get_licence, mocker):
    instance = TEST_LICENCE

    mock_get_licence.return_value = instance

    mocker.patch.object(instance, "full_clean", side_effect=ValidationError("field error message"))

    expected_error_message = "Licence validation error: field error message"

    with pytest.raises(DataIntegrityError) as e:
        licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert e.value.args[0] == expected_error_message


def test_get_licence_by_licence_code_throws_exception_more_than_one_licence_found(mock_get_licence):
    mock_get_licence.side_effect = Licence.MultipleObjectsReturned()

    expected_error_message = f"More than one licence found for licence code: {TEST_LICENCE.licence_code}"

    with pytest.raises(DataIntegrityError) as e:
        licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert e.value.args[0] == expected_error_message


def test_get_licence_by_licence_code_throws_exception_database_error(mock_get_licence):
    mock_get_licence.side_effect = DatabaseError()

    expected_error_message = f"DocumentDB error fetching licence: {TEST_LICENCE.licence_code}"

    with pytest.raises(DocumentDBError) as e:
        licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    assert e.value.args[0] == expected_error_message


def test_get_all_licences_from_database_throws_exception_validation_error(mocker, mock_get_all):
    mock_get_all.return_value = [TEST_LICENCE]

    mocker.patch.object(TEST_LICENCE, "full_clean", side_effect=ValidationError("field error message"))

    expected_error_message = "Licence validation error: field error message"

    with pytest.raises(DataIntegrityError) as e:
        licence_repository.get_all_licences()
    assert e.value.args[0] == expected_error_message


def test_get_all_licences_from_database_throws_database_error(mock_get_all):
    mock_get_all.side_effect = DatabaseError()

    expected_error_message = "DocumentDB error fetching all licences"

    with pytest.raises(DocumentDBError) as e:
        licence_repository.get_all_licences()

    assert e.value.args[0] == expected_error_message


def test_get_all_licences_from_database_calls_database_with_correct_method(mock_get_all):
    licence_repository.get_all_licences()

    mock_get_all.assert_called_once()
