from common.models.interaction_customisations import Customisation, InteractionCustomisation


def find_published_customisation(
    authority_url_slug: str, licence_code: str, interaction_id: int, interaction_sub_id: int
) -> list[Customisation]:
    interaction_customisations = find_interaction_customisations(
        authority_url_slug, licence_code, interaction_id, interaction_sub_id
    )
    published_customisations = [
        interaction_customisation.published_customisation
        for interaction_customisation in interaction_customisations
        if interaction_customisation.published_customisation
        and not interaction_customisation.published_customisation.suspended_at
    ]
    # TODO should this ever be more than one

    return published_customisations


def find_interaction_customisations(
    authority_url_slug: str, licence_code: str, interaction_id: int, interaction_sub_id: int
) -> list[InteractionCustomisation]:
    customisations = list(
        InteractionCustomisation.objects.filter(
            authority_url_slug=authority_url_slug,
            licence_code=licence_code,
            interaction_id=interaction_id,
            interaction_sub_id=interaction_sub_id,
        )
    )
    return customisations
