import logging

from common.models.authorities import Authority
from django.core.exceptions import ValidationError

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
            authority.clean()

        return authorities
    except ValidationError:
        logger.error("Authority does not match model")


def find_authority_by_url_slug(url_slug: str) -> Authority | None:
    try:
        authority = Authority.objects.get(url_slug=url_slug)
        authority.clean()
        return authority
    except ValidationError:
        logger.error("Authority does not match model")
        # TODO return a custom error
        raise FileNotFoundError("Temporary authority does not exist") from None
    except Authority.DoesNotExist:
        return None
