import pytest

from citizen_frontend.api.utils import get_country_from_geographical_locator


@pytest.mark.parametrize(
    "country,snac_codes",
    [
        ("England", ["00CX", "38", "24UH", "00AK", "00DA"]),
        ("NI", ["95A", "95S", "95J", "95D", "95I"]),
        ("Scotland", ["00RD", "00RH", "00QZ", "00QJ", "00QN"]),
        ("Wales", ["00NS", "00NZ", "00PM", "00PB", "00PP"]),
    ],
)
def test_get_country_from_geographical_locator_returns_correct_country_for_snac_code(country, snac_codes):
    for snac_code in snac_codes:
        assert get_country_from_geographical_locator(snac_code) == country


@pytest.mark.parametrize(
    "country,gss_codes",
    [
        ("England", ["E00000000", "E12345678", "E99999999"]),
        ("NI", ["N00000000", "N12345678", "N99999999"]),
        ("Scotland", ["S00000000", "S12345678", "S99999999"]),
        ("Wales", ["W00000000", "W12345678", "W99999999"]),
    ],
)
def test_get_country_from_geographical_locator_returns_correct_country_for_gss_code(country, gss_codes):
    for gss_code in gss_codes:
        assert get_country_from_geographical_locator(gss_code) == country


def test_get_country_from_geographical_locator_returns_none_for_invalid_locator():
    invalid_geographical_locator = "invalid"
    assert get_country_from_geographical_locator(invalid_geographical_locator) is None
