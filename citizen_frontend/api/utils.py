import re

from common.enums.countries import Countries
from common.enums.snac_codes import SnacCodes
from common.models.licences import Licence

# Should these exist in common/go into separate file
COUNTRY_TO_SNAC_CODE = {
    Countries.ENGLAND: SnacCodes.ENGLAND.value,
    Countries.WALES: SnacCodes.WALES.value,
    Countries.NORTHERN_IRELAND: SnacCodes.NORTHERN_IRELAND.value,
    Countries.SCOTLAND: SnacCodes.SCOTLAND.value,
}

# should we be doing an external call rather than relying on a regex...
# How do we even know this is a valid code that exists...
COUNTRY_TO_GSS_CODE = {
    Countries.ENGLAND: r"^E\d{8}$",
    Countries.WALES: r"^W\d{8}$",
    Countries.NORTHERN_IRELAND: r"^N\d{8}$",
    Countries.SCOTLAND: r"^S\d{8}$",
}


def get_all_licences_from_database() -> list[Licence]:
    licences = Licence.objects.all()

    for licence in licences:
        licence.clean()

    return list(licences)


def get_country_from_geographical_locator(locator: str):
    for key, value in COUNTRY_TO_SNAC_CODE.items():
        if locator in value:
            return key

    for key, value in COUNTRY_TO_GSS_CODE.items():
        if re.match(value, locator):
            return key

    return None
