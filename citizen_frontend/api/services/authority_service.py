from citizen_frontend.api.repository.authority_repository import AuthorityRepository


class AuthorityService:
    def __init__(self):
        self.authority_repository = AuthorityRepository()

    def get_authorities_for_licence(self, licence_code):
        self.authority_repository.get_licence_offering_authorities_by_licence_code(licence_code=licence_code)
