from common.enums.countries import Countries
from common.enums.snac_codes import SnacCodes
from common.models.licences import Licence

COUNTRY_TO_SNAC_CODE = {
    Countries.ENGLAND: SnacCodes.ENGLAND.value,
    Countries.WALES: SnacCodes.WALES.value,
    Countries.NORTHERN_IRELAND: SnacCodes.NORTHERN_IRELAND.value,
    Countries.SCOTLAND: SnacCodes.SCOTLAND.value,
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
    return None
