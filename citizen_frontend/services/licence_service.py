import logging

from common.models.licence import Licence, LicenceInteraction

from citizen_frontend.exceptions import DataIntegrityError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def find_interaction(licence: Licence, interaction_id: int, interaction_sub_id: int) -> LicenceInteraction | None:
    matching_interactions = [
        interaction
        for interaction in licence.licence_interactions
        if interaction.interaction_id == interaction_id and interaction.interaction_sub_id == interaction_sub_id
    ]
    if len(matching_interactions) > 1:
        logger.error(
            "Found more than one matching interactions for: %s and %s on %s",
            interaction_id,
            interaction_sub_id,
            licence.name,
        )
        raise DataIntegrityError("Multiple matching interactions found")
    return matching_interactions[0] if matching_interactions else None
