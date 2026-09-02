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
def test_get_country_from_geographical_locator_return_correct_country_for_snac_code(country, snac_codes):
    for snac_code in snac_codes:
        assert get_country_from_geographical_locator(snac_code) == country
