from common.models.authority import Authority


class AuthorityRepo:
    def __init__(self):
        self.model = Authority

    def find_authority_by_url_slug(self, slug):
        pass


# class LicenceRepo(DjangoRepository):
#     def __init__(self):
#         super().__init__(Licence)
#
#     def get_licence_by_url_slug(self, slug):
#         pass
#
#
# class DepartmentRepo(DjangoRepository):
#     def __init__(self):
#         super().__init__(Department)
#
#     def get_by_id(self, department_id):
#         try:
#             department = self._get(_id=department_id)
#             department.clean_fields()
#             return department
#         except Department.DoesNotExist as e:
#             raise ObjectDoesNotExist("Department not found") from e
