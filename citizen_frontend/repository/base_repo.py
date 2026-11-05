from common.models.authority import Authority
from common.models.department import Department
from common.models.licence import Licence
from django.core.exceptions import ObjectDoesNotExist


class AuthorityRepo:
    def __init__(self):
        self.model = Authority

    def find_authority_by_url_slug(self, slug):
        pass


class LicenceRepo:
    def __init__(self):
        self.model = Licence

    def get_licence_by_url_slug(self, slug):
        pass


class DepartmentRepo:
    def __init__(self):
        self.model = Department

    def get_by_id(self, department_id):
        try:
            department = self.model.objects.get(_id=department_id)
            department.clean_fields()
            return department
        except Department.DoesNotExist as e:
            raise ObjectDoesNotExist("Department not found") from e
