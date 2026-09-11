from common.models.interaction_customisations import Customisation, InteractionCustomisation


def find_published_customisation(
    authority_url_slug: str, licence_code: str, interaction_id: int, interaction_sub_id: int
) -> Customisation | None:
    interaction_customisation = find_interaction_customisation(
        authority_url_slug, licence_code, interaction_id, interaction_sub_id
    )

    # TODO should this
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
    customisations = list(
        InteractionCustomisation.objects.filter(
            authority_url_slug=authority_url_slug,
            licence_code=licence_code,
            interaction_id=interaction_id,
            interaction_sub_id=interaction_sub_id,
        )
    )
    # TODO error handle when more than one or verify there's never more than one
    if customisations:
        return customisations[0]
    return None
