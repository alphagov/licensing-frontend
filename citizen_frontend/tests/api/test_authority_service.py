from copy import deepcopy

import pytest
from common.enums.countries import Countries
from conftest import TEST_AUTHORITY, TEST_LICENCE_CODE, TEST_SNAC_CODE, TEST_TEMP_EVENT_LICENCE

from citizen_frontend.api.services.authority_service import AuthorityService


@pytest.fixture
def mock_service(mocker):
    service = AuthorityService()
    mocker.patch.object(service, "authority_repository")
    yield service


def test_get_authorities_for_licence_calls_authority_repository(mock_service):
    mock_service.get_authorities_for_licence(TEST_LICENCE_CODE)

    mock_service.authority_repository.get_licence_offering_authorities_by_licence_code.assert_called_with(
        licence_code=TEST_LICENCE_CODE
    )


def test_get_authorities_for_licence_returns_list_of_authorities(mock_service):
    mock_service.authority_repository.get_licence_offering_authorities_by_licence_code.return_value = [TEST_AUTHORITY]

    authorities = mock_service.get_authorities_for_licence(TEST_LICENCE_CODE)

    assert authorities == [TEST_AUTHORITY]


def test_get_authorities_for_licence_with_geographical_locator_calls_get_country(mock_service, mocker):
    mocker.patch.object(mock_service, "get_country_from_geographical_locator")

    mock_service.get_authorities_for_licence_with_geographical_locator(
        locator=TEST_SNAC_CODE, licence=TEST_TEMP_EVENT_LICENCE
    )

    mock_service.get_country_from_geographical_locator.assert_called_with(locator=TEST_SNAC_CODE)


def test_get_authorities_for_licence_with_locator_calls_get_authorities_for_licence_licence_admin_area_contains_country(
    mock_service, mocker
):
    mocker.patch.object(mock_service, "get_country_from_geographical_locator", return_value=Countries.ENGLAND)
    mocker.patch.object(mock_service, "get_authorities_for_licence")

    mock_service.get_authorities_for_licence_with_geographical_locator(
        locator=TEST_LICENCE_CODE, licence=TEST_TEMP_EVENT_LICENCE
    )

    mock_service.get_authorities_for_licence.assert_called_with(licence_code=TEST_LICENCE_CODE)


def test_get_authorities_with_locator_does_not_get_authorities_licence_admin_area_does_not_contain_country(
    mock_service, mocker
):
    mocker.patch.object(mock_service, "get_country_from_geographical_locator", return_value=Countries.NORTHERN_IRELAND)
    mocker.patch.object(mock_service, "get_authorities_for_licence")

    mock_service.get_authorities_for_licence_with_geographical_locator(
        locator=TEST_LICENCE_CODE, licence=TEST_TEMP_EVENT_LICENCE
    )
    mock_service.get_authorities_for_licence.assert_not_called()


def test_check_authority_covers_location_returns_true_locator_present(mock_service):
    test_authority_with_snac_codes = deepcopy(TEST_AUTHORITY)
    test_authority_with_snac_codes.snac_codes = [TEST_SNAC_CODE]

    actual = mock_service.check_authority_covers_location(
        authority=test_authority_with_snac_codes,
        locator=TEST_SNAC_CODE,
        country=Countries.ENGLAND,
    )

    assert actual


def test_check_authority_covers_location_returns_true_country_present(mock_service):
    test_authority_with_snac_codes = deepcopy(TEST_AUTHORITY)
    test_authority_with_snac_codes.snac_codes = [TEST_SNAC_CODE]

    actual = mock_service.check_authority_covers_location(
        authority=test_authority_with_snac_codes,
        locator=TEST_SNAC_CODE,
        country=Countries.ENGLAND,
    )

    assert actual


def test_check_authority_covers_location_returns_false_country_not_present(mock_service):
    test_authority_with_snac_codes = deepcopy(TEST_AUTHORITY)
    test_authority_with_snac_codes.snac_codes = [TEST_SNAC_CODE]

    actual = mock_service.check_authority_covers_location(
        authority=test_authority_with_snac_codes,
        locator=TEST_SNAC_CODE,
        country=Countries.NORTHERN_IRELAND,
    )

    assert not actual


def test_check_authority_covers_location_returns_true_country_present_snac_codes_empty(mock_service):
    actual = mock_service.check_authority_covers_location(
        authority=TEST_AUTHORITY,
        locator=TEST_SNAC_CODE,
        country=Countries.ENGLAND,
    )

    assert actual


@pytest.mark.parametrize(
    "country,snac_codes",
    [
        ("England", ["00CX", "38", "24UH", "00AK", "00DA"]),
        ("NI", ["95A", "95S", "95J", "95D", "95I"]),
        ("Scotland", ["00RD", "00RH", "00QZ", "00QJ", "00QN"]),
        ("Wales", ["00NS", "00NZ", "00PM", "00PB", "00PP"]),
    ],
)
def test_get_country_from_geographical_locator_returns_correct_country_for_snac_code(country, snac_codes, mock_service):
    for snac_code in snac_codes:
        assert mock_service.get_country_from_geographical_locator(snac_code) == country


@pytest.mark.parametrize(
    "country,gss_codes",
    [
        ("England", ["E00000000", "E12345678", "E99999999"]),
        ("NI", ["N00000000", "N12345678", "N99999999"]),
        ("Scotland", ["S00000000", "S12345678", "S99999999"]),
        ("Wales", ["W00000000", "W12345678", "W99999999"]),
    ],
)
def test_get_country_from_geographical_locator_returns_correct_country_for_gss_code(country, gss_codes, mock_service):
    for gss_code in gss_codes:
        assert mock_service.get_country_from_geographical_locator(gss_code) == country


def test_get_country_from_geographical_locator_returns_none_for_invalid_locator(mock_service):
    invalid_geographical_locator = "invalid"
    assert mock_service.get_country_from_geographical_locator(invalid_geographical_locator) is None
