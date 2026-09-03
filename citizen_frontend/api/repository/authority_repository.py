import logging

from common.models.authorities import Authority
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class AuthorityRepository:
    @staticmethod
    def get_licence_offering_authorities_by_licence_code(licence_code: str) -> list[Authority]:
        try:
            authorities = list(
                Authority.objects.filter(
                    licence_details__licence_code=licence_code, licence_details__offered_by_authority=True
                )
            )

            for authority in authorities:
                authority.clean()

            return authorities
        except ValidationError:
            logger.error("Authority does not match model")
