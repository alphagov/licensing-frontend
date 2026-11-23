import datetime
import logging

from common.models.authority import Authority
from common.models.interaction_customisation import Customisation
from common.models.licence import Licence, LicenceInteraction
from common.models.licence_application import ApplicationStatus, LicenceApplication, Service, SupportingDocument
from django.core.exceptions import ValidationError
from django.db import DatabaseError, connection
from django.utils import timezone
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
            count = self.counter_repo.get_next_count()
            logger.info("Creating new licence application entry %s-%s", authority.url_slug, count)

            service = Service(
                licence_code=licence.licence_code,
                interaction_id=interaction.interaction_id,
                interaction_sub_id=interaction.interaction_sub_id,
            )

            has_fixed_fee_amount = customisation.fixed_fee_amount and customisation.fixed_fee_amount.pence > 0

            # TODO create method/util/function to handle working days, does python do this?
            now = timezone.now()
            expected_process_date = (
                now + datetime.timedelta(days=customisation.number_of_days_to_process)
                if customisation.number_of_days_to_process
                else now + datetime.timedelta(days=30)
            )

            new_application_entry = LicenceApplication(
                applicant_email=email,
                authority=authority.url_slug,
                application_reference_number=f"{authority.url_slug}-{count}",
                licence=licence.url_slug,
                has_supporting_documents_online=is_supporting_documents_online,
                application_pdf=application_document,
                service=service,
                has_tacit_consent=customisation.has_tacit_consent,
                is_fee_required=customisation.is_fee_required,
                required_payment_amount=customisation.fixed_fee_amount,
                supporting_documents=supporting_documents,
                has_variable_fee=customisation.is_fee_required and not has_fixed_fee_amount,
                application_status=ApplicationStatus(),
                expected_processing_date=expected_process_date,
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

    def calculate_expected_processing_date(self, processing_days, is_working_days) -> datetime.datetime:
        day = timezone.now() + datetime.timedelta(days=processing_days)
        return day.date()


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
