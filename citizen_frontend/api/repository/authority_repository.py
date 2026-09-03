from common.models.authorities import Authority


class AuthorityRepository:
    @staticmethod
    def get_licence_offering_authorities_by_licence_code(licence_code: str) -> list[Authority]:
        return list(
            Authority.objects.filter(
                licence_details__licence_code=licence_code, licence_details__offered_by_authority=True
            )
        )
