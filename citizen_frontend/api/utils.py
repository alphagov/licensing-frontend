from common.enums.countries import Countries
from common.enums.interaction_id_codes import InteractionIdCodes
from common.enums.snac_codes import SnacCodes
from common.models.licences import Licence

from citizen_frontend.enums.licence_interactions import LicenceInteractions

COUNTRY_TO_SNAC_CODE = {
    Countries.ENGLAND: SnacCodes.ENGLAND.value,
    Countries.WALES: SnacCodes.WALES.value,
    Countries.NORTHERN_IRELAND: SnacCodes.NORTHERN_IRELAND.value,
    Countries.SCOTLAND: SnacCodes.SCOTLAND.value,
}

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


INTERACTION_ID_WORD_MAPPING = {InteractionIdCodes.APPLY: LicenceInteractions.APPLY}
