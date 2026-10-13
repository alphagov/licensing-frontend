import logging

from common.models.interaction_customisation import Customisation, InteractionCustomisation
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def find_published_customisation(
    authority_url_slug: str, licence_code: str, interaction_id: int, interaction_sub_id: int
) -> Customisation | None:
    logger.info(
        "Finding published customisation for: %s, %s, %s, %s",
        authority_url_slug,
        licence_code,
        interaction_id,
        interaction_sub_id,
    )
    interaction_customisation = find_interaction_customisation(
        authority_url_slug, licence_code, interaction_id, interaction_sub_id
    )
    if (
        interaction_customisation
        and interaction_customisation.published_customisation
        and not interaction_customisation.published_customisation.suspended_at
    ):
        return interaction_customisation.published_customisation

    logger.info("No published customisation found")
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

        if customisation:
            customisation.full_clean()
            return customisation
        return None
    except ValidationError as e:
        logger.error(e)
        raise DataIntegrityError(f"InteractionCustomisation validation error: {e.message}") from e
    except InteractionCustomisation.MultipleObjectsReturned as e:
        logger.error(e)
        raise DataIntegrityError(
            f"More than one InteractionCustomisations found for the following "
            f"arguments:"
            f"{authority_url_slug}, {licence_code}, {interaction_id}, "
            f"{interaction_sub_id}"
        ) from e
    except DatabaseError as e:
        logger.error(e)
        raise DocumentDBError("There was a database error accessing InteractionCustomisations collection") from e
