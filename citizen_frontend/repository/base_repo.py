from common.models.authority import Authority
from common.models.department import Department
from common.models.licence import Licence
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


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

    def get_by_id(self, department_id) -> Department:
        try:
            department = self.model.objects.get(_id=department_id)
            department.clean_fields()
            return department
        except Department.DoesNotExist as e:
            raise ObjectDoesNotExist("Department not found") from e


# TODO what does this actually look like?
class Settings(models.Model):
    key = models.CharField(max_length=255, unique=True)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = "settings"
        managed = False

    def __str__(self):
        return f"{self.key}: {self.value}"


class SettingsRepo:
    def __init__(self):
        self.model = Settings

    def get_setting(self, key) -> Settings:
        try:
            setting = self.model.objects.get(id=key)
            return setting
        except self.model.DoesNotExist as e:
            raise ObjectDoesNotExist("Settings not found") from e
