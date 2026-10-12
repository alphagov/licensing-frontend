from common.models.licence import Licence, LicenceInteraction


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
