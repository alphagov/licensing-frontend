import logging

from common.models.licence import Licence
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LicenceRepository:
    def __init__(self):
        self.model = Licence

    def get_licence_by_url_slug(self, url_slug: str) -> Licence:
        try:
            licence = self.model.objects.get(url_slug=url_slug)
            licence.clean_fields()
            return licence
        except ValidationError as e:
            logger.error("Licence does not match model")
            raise DataIntegrityError(f"Licence validation error: {e.messages}") from e
        except DatabaseError as e:
            logger.error("DocumentDB error fetching licence: %s", e)
            raise DocumentDBError("DocumentDB error fetching licence") from e
        except Licence.DoesNotExist as e:
            raise ObjectDoesNotExist(f"Licence does not exist: {url_slug}") from e

    def get_all_licences(self) -> list[Licence]:
        try:
            licences = list(self.model.objects.all())

            for licence in licences:
                licence.clean_fields()

            return licences
        except ValidationError as e:
            logger.error(e.messages)
            raise DataIntegrityError(f"Licence validation error: {e.messages}") from e
        except DatabaseError as e:
            logger.error(e)
            raise DocumentDBError("DocumentDB error fetching all licences") from e

    def get_licence_by_licence_code(self, licence_code: str) -> Licence | None:
        try:
            logger.info("Getting licence by licence code: %s", licence_code)
            licence = self.model.objects.get(licence_code=licence_code)
            if licence:
                licence.clean_fields()
                return licence
        except Licence.DoesNotExist:
            logger.info("No licence found for licence code: %s", licence_code)
            return None
        except Licence.MultipleObjectsReturned as e:
            logger.error("Multiple licences with licence code: %s", licence_code)
            raise DataIntegrityError(f"More than one licence found for licence code: {licence_code}") from e
        except ValidationError as e:
            logger.error(e.messages)
            raise DataIntegrityError(f"Licence validation error: {e.messages}") from e
        except DatabaseError as e:
            logger.error("An error occurred while getting licence with code %s: %s", licence_code, e)
            raise DocumentDBError(f"DocumentDB error fetching licence: {licence_code}") from e
