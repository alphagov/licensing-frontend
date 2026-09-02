from citizen_frontend.api.repository.authority_repository import AuthorityRepository


class AuthorityService:
    def __init__(self):
        self.authority_repository = AuthorityRepository()

    def get_authorities_for_licence(self):
        self.authority_repository.get_offering_authorities_by_licence_code()
