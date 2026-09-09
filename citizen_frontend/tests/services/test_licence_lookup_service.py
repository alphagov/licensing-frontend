from copy import deepcopy

import bson
from common.models.interaction_customisations import Customisation
from common.models.shared_models import PaymentAmount
from conftest import TEST_CUSTOMISATION_FIXED_FEE, TEST_CUSTOMISATION_VARIABLE_FEE
from django.utils import timezone

from citizen_frontend.enums.payment_type import PaymentType
from citizen_frontend.services.licence_lookup_service import LicenceLookupService
from citizen_frontend.tests.conftest import BASE_URL, TEST_AUTHORITY, TEST_LICENCE


def test_get_licence_url_when_authority_uses_gov_uk():
    licence_lookup_service = LicenceLookupService()
    result = licence_lookup_service.get_licence_url(
        licence_interaction=TEST_LICENCE.licence_interactions[0],
        licence=TEST_LICENCE,
        authority=TEST_AUTHORITY,
        uses_gov_uk=TEST_AUTHORITY.licence_details[0].using_gov_uk,
    )

    assert result == f"{BASE_URL}/apply-for-a-licence/test-licence/test-authority/apply-1"


def test_get_licence_url_when_authority_does_not_use_gov_uk():
    test_authority_not_using_gov_uk = deepcopy(TEST_AUTHORITY)
    test_authority_not_using_gov_uk.licence_details[0].using_gov_uk = False
    test_authority_not_using_gov_uk.licence_details[0].authority_url = "test-authority.gov.uk"
    licence_lookup_service = LicenceLookupService()

    result = licence_lookup_service.get_licence_url(
        licence_interaction=TEST_LICENCE.licence_interactions[0],
        licence=TEST_LICENCE,
        authority=test_authority_not_using_gov_uk,
        uses_gov_uk=test_authority_not_using_gov_uk.licence_details[0].using_gov_uk,
    )

    assert result == test_authority_not_using_gov_uk.licence_details[0].authority_url


def test_get_licence_url_returns_empty_string_when_no_matched_licence_details_found():
    test_authority_with_non_matching_licence_details = deepcopy(TEST_AUTHORITY)
    test_authority_with_non_matching_licence_details.licence_details[0].using_gov_uk = False
    test_authority_with_non_matching_licence_details.licence_details[0].authority_url = "test-authority.gov.uk"
    test_authority_with_non_matching_licence_details.licence_details[0].licence_code = "345-6-7"
    licence_lookup_service = LicenceLookupService()

    result = licence_lookup_service.get_licence_url(
        licence_interaction=TEST_LICENCE.licence_interactions[0],
        licence=TEST_LICENCE,
        authority=test_authority_with_non_matching_licence_details,
        uses_gov_uk=test_authority_with_non_matching_licence_details.licence_details[0].using_gov_uk,
    )

    assert result == ""


def test_get_licence_url_returns_empty_string_when_authority_url_is_empty():
    test_authority_with_empty_authority_url = deepcopy(TEST_AUTHORITY)
    test_authority_with_empty_authority_url.licence_details[0].using_gov_uk = False
    test_authority_with_empty_authority_url.licence_details[0].authority_url = ""
    licence_lookup_service = LicenceLookupService()

    result = licence_lookup_service.get_licence_url(
        licence_interaction=TEST_LICENCE.licence_interactions[0],
        licence=TEST_LICENCE,
        authority=test_authority_with_empty_authority_url,
        uses_gov_uk=test_authority_with_empty_authority_url.licence_details[0].using_gov_uk,
    )

    assert result == ""


def test_get_payment_type_from_customisation_when_no_fee_required():
    customisation_no_fee_required = deepcopy(TEST_CUSTOMISATION_VARIABLE_FEE)
    customisation_no_fee_required.is_fee_required = False

    licence_lookup_service = LicenceLookupService()

    actual = licence_lookup_service.get_payment_type_from_customisation(customisation_no_fee_required)

    assert actual == PaymentType.NONE


def test_get_payment_type_from_customisation_when_fixed_fee_required():
    customisation_fixed_fee_required = Customisation(
        is_postal_allowed=False,
        number_of_days_to_process=30,
        is_processing_days_working_days=True,
        has_tacit_consent=False,
        created_at=timezone.now(),
        fixed_fee_amount=PaymentAmount(pence=500),
        is_fee_required=True,
        legislation_name="test-legislation",
        introduction_text="test-introduction",
        declarations=["test-declaration1", "test-declaration2"],
        department=bson.ObjectId(),
    )

    licence_lookup_service = LicenceLookupService()

    actual = licence_lookup_service.get_payment_type_from_customisation(customisation_fixed_fee_required)

    assert actual == PaymentType.FIXED_FEE


def test_get_payment_type_from_customisation_returns_variable_fee_when_no_fixed_fee_but_fee_required():
    licence_lookup_service = LicenceLookupService()

    actual = licence_lookup_service.get_payment_type_from_customisation(TEST_CUSTOMISATION_VARIABLE_FEE)

    assert actual == PaymentType.VARIABLE_FEE


def test_get_payment_type_from_customisation_returns_variable_fee_when_fixed_fee_amount_is_0_and_fee_required():
    customisation_fixed_fee_zero_pence = Customisation(
        is_postal_allowed=False,
        number_of_days_to_process=30,
        is_processing_days_working_days=True,
        has_tacit_consent=False,
        created_at=timezone.now(),
        fixed_fee_amount=PaymentAmount(),
        is_fee_required=True,
        legislation_name="test-legislation",
        introduction_text="test-introduction",
        declarations=["test-declaration1", "test-declaration2"],
        department=bson.ObjectId(),
    )

    licence_lookup_service = LicenceLookupService()

    actual = licence_lookup_service.get_payment_type_from_customisation(customisation_fixed_fee_zero_pence)

    assert actual == PaymentType.VARIABLE_FEE


def test_get_payment_amount_from_customisation_returns_fee_amount_when_fixed_fee_is_required():
    licence_lookup_service = LicenceLookupService()

    actual = licence_lookup_service.get_payment_amount_from_customisation(TEST_CUSTOMISATION_FIXED_FEE)

    assert actual == TEST_CUSTOMISATION_FIXED_FEE.fixed_fee_amount


def test_get_payment_amount_from_customisation_returns_none_when_no_fee_required():
    customisation_no_fee_required = deepcopy(TEST_CUSTOMISATION_VARIABLE_FEE)
    customisation_no_fee_required.is_fee_required = False
    licence_lookup_service = LicenceLookupService()

    actual = licence_lookup_service.get_payment_amount_from_customisation(customisation_no_fee_required)

    assert actual is None


def test_get_payment_amount_from_customisation_returns_none_when_no_fee_required_but_fixed_fee_exists():
    customisation_fixed_fee_not_required = deepcopy(TEST_CUSTOMISATION_FIXED_FEE)
    customisation_fixed_fee_not_required.is_fee_required = False
    licence_lookup_service = LicenceLookupService()

    actual = licence_lookup_service.get_payment_amount_from_customisation(customisation_fixed_fee_not_required)

    assert actual is None
