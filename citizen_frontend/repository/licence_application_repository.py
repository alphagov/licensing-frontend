from common.models.authority import Authority
from common.models.interaction_customisation import Customisation
from common.models.licence import Licence, LicenceInteraction
from common.models.licence_application import LicenceApplication, SupportingDocument
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError


class LicenceApplicationRepository:
    def __init__(self):
        self.model = LicenceApplication

    def get_application_from_id(self, application_id):
        try:
            application = self.model.objects.get(application_reference_number=application_id)
            application.clean_fields()
            return application
        except ValidationError as e:
            raise DataIntegrityError from e
        except DatabaseError as e:
            raise DocumentDBError from e

    def create_new_licence_application(
        self,
        email: str,
        application_document: SupportingDocument,
        supporting_documents: list[SupportingDocument],
        authority: Authority,
        licence: Licence,
        customisation: Customisation,
        interaction: LicenceInteraction,
        is_supporting_documents_online: bool,
    ):
        pass
