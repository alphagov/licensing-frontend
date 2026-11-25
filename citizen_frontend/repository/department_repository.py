from common.models.department import Department
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import DatabaseError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError


class DepartmentRepository:
    def __init__(self):
        self.model = Department

    def get_department_from_authority_slug(self, authority_slug) -> Department:
        try:
            department = self.model.objects.get(authority_slug=authority_slug)
            department.clean_fields()
            return department
        except ValidationError as e:
            raise DataIntegrityError from e
        except DatabaseError as e:
            raise DocumentDBError from e

    def get_department_by_id(self, department_id) -> Department:
        try:
            department = self.model.objects.get(_id=department_id)
            department.clean_fields()
            return department
        except Department.DoesNotExist as e:
            raise ObjectDoesNotExist("Department not found") from e
