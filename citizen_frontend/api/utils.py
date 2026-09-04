from common.enums.interaction_id_codes import InteractionIdCodes
from common.models.licences import Licence

from citizen_frontend.enums.licence_interactions import LicenceInteractions


def get_all_licences_from_database() -> list[Licence]:
    licences = Licence.objects.all()

    for licence in licences:
        licence.clean()

    return list(licences)


INTERACTION_ID_WORD_MAPPING = {InteractionIdCodes.APPLY: LicenceInteractions.APPLY}
