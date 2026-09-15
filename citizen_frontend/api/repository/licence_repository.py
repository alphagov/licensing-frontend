import logging

from common.models.licences import Licence
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_licence_by_url_slug(url_slug: str) -> Licence:
    try:
        licence = Licence.objects.get(url_slug=url_slug)
        licence.clean()
        return licence
    except ValidationError:
        logger.error("Licence does not match model")
        # TODO return a custom error
        raise FileNotFoundError("Temporary licence does not exist") from None
    except Licence.DoesNotExist:
        # TODO return a custom error
        raise FileNotFoundError("Temporary licence does not exist") from None
