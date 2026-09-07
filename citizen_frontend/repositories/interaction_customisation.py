from licensing_common.common.models.interaction_customisations import InteractionCustomisation


class InteractionCustomisationRepository:
    @staticmethod
    def _base_find_interaction_customisation(
        authority_slug_url: str, licence_code: str, interaction_id: int, interaction_sub_id: int
    ):
        return InteractionCustomisation.objects.filter(
            authority_slug_url=authority_slug_url,
            licence_code=licence_code,
            interaction_id=interaction_id,
            interaction_sub_id=interaction_sub_id,
        )

    @classmethod
    def find_published_interaction_customisation(
        cls, authority_slug_url: str, licence_code: str, interaction_id: int, interaction_sub_id: int
    ) -> InteractionCustomisation | None:
        interaction_with_published_customisation_query = cls._base_find_interaction_customisation(
            authority_slug_url, licence_code, interaction_id, interaction_sub_id
        ).filter(published=True)
        interaction_with_published_customisation = interaction_with_published_customisation_query.first()
        return (
            interaction_with_published_customisation.published_customisation
            if interaction_with_published_customisation
            else None
        )

    @classmethod
    def find_interaction_customisation(
        cls, authority_slug_url: str, licence_code: str, interaction_id: int, interaction_sub_id: int
    ) -> InteractionCustomisation | None:
        customisation = cls._base_find_interaction_customisation(
            authority_slug_url, licence_code, interaction_id, interaction_sub_id
        ).first()
        return customisation
