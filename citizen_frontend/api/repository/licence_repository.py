import logging

from common.models.licences import Licence
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from citizen_frontend.exceptions import DataError, DocumentDBError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_all_licences_from_database() -> list[Licence]:
    licences = list(Licence.objects.all())

    for licence in licences:
        licence.clean()

    return licences


def get_licence_by_licence_code(licence_code: str) -> Licence | None:
    try:
        logger.info("Getting licence by licence code: %s", licence_code)
        licence = Licence.objects.get(licence_code=licence_code)
        if licence:
            licence.full_clean()
            return licence
    except Licence.DoesNotExist:
        logger.info("No licence found for licence code: %s", licence_code)
        return None
    except Licence.MultipleObjectsReturned as e:
        logger.error("Multiple licences with licence code: %s", licence_code)
        raise DataError(f"More than one licence found for licence code: {licence_code}") from e
    except ValidationError as e:
        logger.error(e.message)
        raise DataError(f"Licence validation error: {e.message}") from e
    except DatabaseError as e:
        logger.error("An error occurred while getting licence with code %s: %s", licence_code, e)
        raise DocumentDBError(f"DocumentDB error fetching licence: {licence_code}") from e
