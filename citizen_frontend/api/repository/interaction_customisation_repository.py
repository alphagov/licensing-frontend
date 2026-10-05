import logging

from common.models.interaction_customisations import Customisation, InteractionCustomisation
from django.core.exceptions import ValidationError

from citizen_frontend.exceptions import InteractionCustomisationDataError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def find_published_customisation(
    authority_url_slug: str, licence_code: str, interaction_id: int, interaction_sub_id: int
) -> Customisation | None:
    interaction_customisation = find_interaction_customisation(
        authority_url_slug, licence_code, interaction_id, interaction_sub_id
    )
    if (
        interaction_customisation
        and interaction_customisation.published_customisation
        and not interaction_customisation.published_customisation.suspended_at
    ):
        return interaction_customisation.published_customisation
    return None


def find_interaction_customisation(
    authority_url_slug: str, licence_code: str, interaction_id: int, interaction_sub_id: int
) -> InteractionCustomisation | None:
    try:
        customisation = InteractionCustomisation.objects.get(
            authority_url_slug=authority_url_slug,
            licence_code=licence_code,
            interaction_id=interaction_id,
            interaction_sub_id=interaction_sub_id,
        )
        # TODO error handle when more than one or verify there's never more than one
        if customisation:
            customisation.full_clean()
            return customisation
        return None
    except ValidationError as e:
        logger.error(e)
        raise InteractionCustomisationDataError(f"InteractionCustomisation validation error: {e.message}") from e
