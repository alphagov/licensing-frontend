import logging

from common.models.authority import Authority
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AuthorityRepository:
    def __init__(self):
        self.model = Authority

    def get_licence_offering_authorities_by_licence_code(self, licence_code: str) -> list[Authority]:
        try:
            authorities = list(
                self.model.objects.filter(
                    licence_details__licence_code=licence_code, licence_details__offered_by_authority=True
                )
            )

            for authority in authorities:
                authority.clean_fields()

            return authorities
        except ValidationError as e:
            logger.error("Authority does not match model")
            raise DataIntegrityError(f"Authority validation error: {e.messages}") from e
        except DatabaseError as e:
            logger.error("There was a database error: %s", e)
            raise DocumentDBError("There was a database error accessing Authorities collection") from e

    def find_authority_by_url_slug(self, url_slug: str) -> Authority | None:
        try:
            authority = self.model.objects.get(url_slug=url_slug)
            authority.clean_fields()
            return authority
        except ValidationError as e:
            logger.error("Authority does not match model")
            raise DataIntegrityError(f"Authority validation error: {e.messages}") from e
        except DatabaseError as e:
            logger.error("There was a database error: %s", e)
            raise DocumentDBError("There was a database error accessing Authorities collection") from e
        except Authority.DoesNotExist:
            return None
