import logging

import bson
from common.models.authority import Authority
from common.models.interaction_customisation import Customisation
from common.models.licence import Licence, LicenceInteraction
from common.models.licence_application import LicenceApplication, Service, SupportingDocument
from django.core.exceptions import ValidationError
from django.db import DatabaseError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
        try:
            entry_id = bson.ObjectId()
            logger.info("Creating new licence application entry %s", entry_id)

            service = Service(
                licence_code=licence.licence_code,
                interaction_id=interaction.interaction_id,
                interaction_sub_id=interaction.interaction_sub_id,
            )

            new_application_entry = LicenceApplication(
                _id=entry_id,
                applicant_email=email,
                authority=authority.url_slug,
                licence=licence.url_slug,
                has_supporting_documents_online=is_supporting_documents_online,
                application_pdf=application_document,
                service=service,
                has_tacit_consent=customisation.has_tacit_consent,
                is_fee_required=customisation.is_fee_required,
                required_payment_amount=customisation.fixed_fee_amount,
                supporting_documents=supporting_documents,
            )

            new_application_entry.full_clean()
            new_application_entry.save()

            return entry_id
        except ValidationError as e:
            logger.error("Failed to create new licence application entry %s, validation error: %s", entry_id, e)
            raise DataIntegrityError from e
        except DatabaseError as e:
            logger.error("Failed to create new licence application entry %s, database error: %s", entry_id, e)
            raise DocumentDBError("Failed to create new object") from e
