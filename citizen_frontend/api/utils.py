from common.enums.countries import Countries
from common.enums.interaction_id_codes import InteractionIdCodes
from common.enums.snac_codes import SnacCodes

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

INTERACTION_ID_WORD_MAPPING = {
    InteractionIdCodes.APPLY: LicenceInteractions.APPLY,
    InteractionIdCodes.PAY_FOR: LicenceInteractions.PAY_FOR,
    InteractionIdCodes.INFORMATION: LicenceInteractions.INFORMATION,
    InteractionIdCodes.REGULATION: LicenceInteractions.REGULATION,
    InteractionIdCodes.CHANGE: LicenceInteractions.CHANGE,
    InteractionIdCodes.RENEW: LicenceInteractions.RENEW,
    InteractionIdCodes.APPLY_FOR_EXEMPTION: LicenceInteractions.APPLY_FOR_EXEMPTION,
    InteractionIdCodes.TELL_US_ONCE: LicenceInteractions.TELL_US_ONCE,
    InteractionIdCodes.NOTIFY_OF_INCIDENT_OR_INSTANCES: LicenceInteractions.NOTIFY_OF_INCIDENT_OR_INSTANCES,
    InteractionIdCodes.UNKNOWN: LicenceInteractions.UNKNOWN,
}
