from django.core.exceptions import ValidationError
from django.db.utils import DatabaseError

from common.models.department import Department
from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError


class DepartmentRepository:
    def __init__(self):
        self.model = Department

    def get_department_from_authority_slug(self, authority_slug):
        try:
            department = self.model.objects.get(authority_slug=authority_slug)
            department.clean_fields()
            return department
        except ValidationError as e:
            raise DataIntegrityError from e
        except DatabaseError as e:
            raise DocumentDBError from e