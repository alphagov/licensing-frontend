from common.models.authorities import Authority


class AuthorityRepository:
    def get_licence_offering_authorities_by_licence_code(self, licence_code):
        return Authority.objects.filter(
            licence_details__licence_code=licence_code, licence_details__offered_by_authority=True
        )
