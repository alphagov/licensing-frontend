import logging

from common.models.licences import Licence
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from citizen_frontend.exceptions import LicenceDataError, LicenceDBError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_licence_by_licence_code(licence_code: str) -> Licence | None:
    try:
        logger.info("Getting licence by licence code: %s", licence_code)
        licence = Licence.objects.get(licence_code=licence_code)
        if licence:
            licence.full_clean()
            return licence
    except Licence.DoesNotExist:
        return None
    except Licence.MultipleObjectsReturned:
        logger.error("Multiple licences with licence code: %s", licence_code)
        raise LicenceDataError("More than one licence found for licence code: %s", licence_code) from None
    except ValidationError as e:
        logger.error(e.message)
        raise LicenceDataError("Licence validation error: %s", e.message) from e
    except DatabaseError as e:
        logger.error(
            "An error occurred while getting licence with code %s: %s",
            licence_code,
            e,
        )
        raise LicenceDBError("DocumentDB error fetching licence: %s", licence_code) from e
