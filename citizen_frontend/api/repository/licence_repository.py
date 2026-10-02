import logging

from common.models.licences import Licence, LicenceInteraction
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


def find_interaction(licence: Licence, interaction_id: int, interaction_sub_id: int) -> LicenceInteraction | None:
    matching_interactions = [
        interaction
        for interaction in licence.licence_interactions
        if interaction.interaction_id == interaction_id and interaction.interaction_sub_id == interaction_sub_id
    ]
    if len(matching_interactions) > 1:
        raise RuntimeError(
            f"Bad data, multiple matching interactions for lgil_id: {interaction_id} "
            f"and lgil_sub_id: {interaction_sub_id} on {licence.name}"
        )

    return matching_interactions[0] if matching_interactions else None
