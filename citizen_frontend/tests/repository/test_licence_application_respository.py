from datetime import datetime, timedelta

import pytest
from common.models.licence_application import SupportingDocument
from common.models.shared_models import SupportingDocumentDefinition
from conftest import (
    TEST_AUTHORITY,
    TEST_CUSTOMISATION_NO_FEE,
    TEST_LICENCE,
    TEST_LICENCE_INTERACTION,
    TEST_UUID,
)
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from freezegun import freeze_time

from citizen_frontend.exceptions import DataIntegrityError, DocumentDBError

VALID_LICENCE_APPLICATION_ARGS = {
    "email": "example@example.com",
    "application_document": SupportingDocument(
        id=f"{TEST_UUID}/file.pdf",
        file_name="file.pdf",
        definition=SupportingDocumentDefinition(
            name="Completed form",
            description="Downloaded and filled PDF form",
            is_mandatory=True,
        ),
    ),
    "supporting_documents": [],
    "authority": TEST_AUTHORITY,
    "licence": TEST_LICENCE,
    "customisation": TEST_CUSTOMISATION_NO_FEE,
    "interaction": TEST_LICENCE_INTERACTION,
    "is_supporting_documents_online": True,
}


def test_create_new_licence_application_calls_db_with_correct_args(mock_licence_application_repo):
    mock_licence_application_repo.model.full_clean.side_effect = None
    mock_licence_application_repo.counter_repo.get_next_count.return_value = 1

    actual = mock_licence_application_repo.create_new_licence_application(**VALID_LICENCE_APPLICATION_ARGS)

    mock_licence_application_repo.model.full_clean.assert_called()
    mock_licence_application_repo.model.save.assert_called()

    assert actual == f"{TEST_AUTHORITY.url_slug}-1"


def test_create_new_licence_application_calls_counter_repository_for_new_count(mock_licence_application_repo):
    mock_licence_application_repo.model.full_clean.side_effect = None

    mock_licence_application_repo.create_new_licence_application(**VALID_LICENCE_APPLICATION_ARGS)

    mock_licence_application_repo.counter_repo.get_next_count.assert_called()


def test_create_new_licence_application_handles_clean_errors(mock_licence_application_repo):
    mock_licence_application_repo.model.full_clean.side_effect = ValidationError("field: error")

    with pytest.raises(DataIntegrityError) as e:
        mock_licence_application_repo.create_new_licence_application(**VALID_LICENCE_APPLICATION_ARGS)

    assert e.value.args[0] == "LicenceApplication validation error: ['field: error'], failed to create new object"


def test_create_new_licence_application_handles_db_errors(mock_licence_application_repo):
    mock_licence_application_repo.model.save.side_effect = DatabaseError

    with pytest.raises(DocumentDBError) as e:
        mock_licence_application_repo.create_new_licence_application(**VALID_LICENCE_APPLICATION_ARGS)

    assert e.value.args[0] == "Failed to create new object, DB error: ()"


def test_calculate_expected_processing_date_only_working_days_false(mock_licence_application_repo):
    number_of_days_to_process = 20
    expected_processing_date = datetime.today() + timedelta(days=number_of_days_to_process)

    actual = mock_licence_application_repo.calculate_expected_processing_date(
        processing_days=number_of_days_to_process,
        is_working_days=False,
    )
    assert actual == expected_processing_date.date()


@freeze_time("2026-11-27")
def test_calculate_expected_processing_date_working_days_true_handles_weekends(mock_licence_application_repo):
    number_of_days_to_process = 2
    expected_processing_date = datetime.fromisoformat("2026-12-01")

    actual = mock_licence_application_repo.calculate_expected_processing_date(
        processing_days=number_of_days_to_process,
        is_working_days=True,
    )

    assert actual == expected_processing_date.date()


@freeze_time("2026-11-08")
def test_calculate_expected_processing_date_5_working_days_sunday_submission_expected_processing_date_is_week_monday(
    mock_licence_application_repo,
):
    expected_date = datetime(2026, 11, 16).date()
    actual = mock_licence_application_repo.calculate_expected_processing_date(
        processing_days=5,
        is_working_days=True,
    )

    assert actual == expected_date


@freeze_time("2026-12-24")
def test_calculate_expected_processing_days_handles_holidays(mock_licence_application_repo):
    expected_date = datetime(2026, 12, 30).date()
    actual = mock_licence_application_repo.calculate_expected_processing_date(
        processing_days=2,
        is_working_days=True,
    )
    assert actual == expected_date


#   test("2020-06-12 shouldn't be a holiday in England, but 2020-03-18 should be one in N.I.") {
#     CalendarApiClient.isBankHoliday("england", LocalDate.parse("2020-06-12")) should be(false)
#     CalendarApiClient.isBankHoliday("ni", LocalDate.parse("2020-03-17")) should be(true)
#   }
#
#   test("2020-01-01 should be a holiday in Wales, but 2020-07-12 shouldn't be one in Scotland") {
#     CalendarApiClient.getBankHolidays("wales") should contain(LocalDate.parse("2020-01-01"))
#     CalendarApiClient.getBankHolidays("Scotland") should not contain (LocalDate.parse("2020-07-12"))
#     CalendarApiClient.getBankHolidays("ni") should contain(LocalDate.parse("2020-07-13"))
#   }
#
#   test("Next working day after Good Thursday is the Tuesday after Easter") {
#     Calendar.plusDaysWithHolidays("England", DateTime.parse("2020-04-09"), 1)
#     should be(LocalDateTime.parse("2020-04-14"))
#   }
#
#   test("7 working days after 2020-12-28 is 2021-01-08 (New Year Holiday)") {
#     Calendar.plusDaysWithHolidays("england", DateTime.parse("2020-12-28"), 7)
#     should be(LocalDateTime.parse("2021-01-08"))
#   }
#
#   test("5 working days after Sunday should be the Monday after next") {
#     Calendar.plusDaysWithHolidays("england", DateTime.parse("2020-07-05"), 5)
#     should be(LocalDateTime.parse("2020-07-13"))
#   }
