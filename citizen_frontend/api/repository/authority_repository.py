import logging

from common.models.authorities import Authority
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from citizen_frontend.exceptions import DataError, DocumentDBError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_licence_offering_authorities_by_licence_code(licence_code: str) -> list[Authority]:
    try:
        authorities = list(
            Authority.objects.filter(
                licence_details__licence_code=licence_code, licence_details__offered_by_authority=True
            )
        )

        for authority in authorities:
            authority.full_clean()

        return authorities
    except ValidationError as e:
        logger.error("Authority does not match model")
        raise DataError(f"Authority validation error: {e.message}") from e
    except DatabaseError as e:
        logger.error("There was a database error: %s", e)
        raise DocumentDBError("There was a database error accessing Authorities collection") from e
