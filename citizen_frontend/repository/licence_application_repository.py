import datetime
import logging

from common.models.licence_application import ApplicationStatus, LicenceApplication, Service, SupportingDocument
from django.core.exceptions import ValidationError
from django.db import DatabaseError, connection
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class LicenceApplicationRepository:
    def __init__(self):
        self.model = LicenceApplication
        self.counter_repo = CounterRepository()

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
        application_submission,
        application_document: SupportingDocument,
        supporting_documents: list[SupportingDocument],
        expected_processing_date: datetime.date,
    ):
        try:
            count = self.counter_repo.get_next_count()
            logger.info(
                "Creating new licence application entry %s-%s", application_submission.authority.url_slug, count
            )

            service = Service(
                licence_code=application_submission.licence.licence_code,
                interaction_id=application_submission.interaction.interaction_id,
                interaction_sub_id=application_submission.interaction.interaction_sub_id,
            )

            has_fixed_fee_amount = (
                application_submission.customisation.fixed_fee_amount
                and application_submission.customisation.fixed_fee_amount.pence > 0
            )

            new_application_entry = LicenceApplication(
                applicant_email=application_submission.email,
                authority=application_submission.authority.url_slug,
                application_reference_number=f"{application_submission.authority.url_slug}-{count}",
                licence=application_submission.licence.url_slug,
                has_supporting_documents_online=application_submission.are_supporting_documents_online,
                application_pdf=application_document,
                service=service,
                has_tacit_consent=application_submission.customisation.has_tacit_consent,
                is_fee_required=application_submission.customisation.is_fee_required,
                required_payment_amount=application_submission.customisation.fixed_fee_amount,
                supporting_documents=supporting_documents,
                has_variable_fee=application_submission.customisation.is_fee_required and not has_fixed_fee_amount,
                application_status=ApplicationStatus(),
                expected_processing_date=expected_processing_date,
            )

            new_application_entry.full_clean()
            new_application_entry.save()

            return new_application_entry.application_reference_number
        except ValidationError as e:
            logger.error(
                "Failed to create new licence application entry %s, validation error: %s",
                new_application_entry.application_reference_number,
                e,
            )
            raise DataIntegrityError(
                f"LicenceApplication validation error: {e.messages}, failed to create new object"
            ) from e
        except (DatabaseError, DocumentDBError) as e:
            # Could get a DB from counters here and then we would not have created the licence application obj yet
            # This would lead to NameError exception I imagine
            logger.error(
                "Failed to create new licence application entry %s, database error: %s",
                new_application_entry.application_reference_number,
                e,
            )
            raise DocumentDBError(f"Failed to create new object, DB error: {e.args}") from e


"""
This counter repository is only called when creating a new licence application object.

It is used to set the, in conjunction with the authority slug of the authority the licence application is for,
licence application application reference number attribute.

The application reference number is used down stream for the following:
   - in a querystring for endpoints that query licence application process and status, and whether payment is due.
   - in the case of a due payment, the creation of unique transaction id for access paysuite.
"""


class CounterRepository:
    @staticmethod
    def get_next_count() -> int:
        try:
            coll = connection.get_collection("counters")
            doc = coll.find_one_and_update(
                {"counterName": "applicationCounter"},
                {"$inc": {"nextId": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
                projection={"nextId": 1},
            )
            return int(doc["nextId"])
        except PyMongoError as e:
            logger.error("Failed to get counter")
            raise DocumentDBError(f"Failed to get counter, DB error: {e}") from e
