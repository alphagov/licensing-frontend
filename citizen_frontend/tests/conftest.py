import os

import pytest
from bson import ObjectId
from common.enums.countries import Countries
from common.models.authorities import Authority, ContactDetails, LicenceDetails
from common.models.licences import AdministrativeArea, Licence, LicenceForm, LicenceInteraction
from common.models.shared_models import PaymentAmount

from citizen_frontend.api.models.api_responses import (
    AuthorityContactDetails,
    AuthorityInteraction,
    IssuingAuthority,
    LicenceAuthoritiesAndInteractionsResponse,
)

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")
SERVICE_SLUG = "apply-for-a-licence"
TEMP_EVENT_SLUG = "temporary-event-notice"
FOOD_PREMISES_APPLICATION_SLUG = "food-premises-approval-6"
TEST_AUTH_SLUG = "winchester"
TEST_INTERACTION = "apply"
TEST_INTERACTION_SUB_ID = "1"

TEST_TEMP_EVENT_APPLY_URL = (
    f"{BASE_URL}/{SERVICE_SLUG}/{TEMP_EVENT_SLUG}/{TEST_AUTH_SLUG}/{TEST_INTERACTION}-{TEST_INTERACTION_SUB_ID}"
)

TEST_FOOD_PREMISES_APPLY_URL = (
    f"{BASE_URL}/{SERVICE_SLUG}/"
    f"{FOOD_PREMISES_APPLICATION_SLUG}/{TEST_AUTH_SLUG}/{TEST_INTERACTION}-{TEST_INTERACTION_SUB_ID}"
)

TEST_TEMP_EVENT_APPLY_FORM_URL = (
    f"/{SERVICE_SLUG}/{TEMP_EVENT_SLUG}/{TEST_AUTH_SLUG}/{TEST_INTERACTION}-{TEST_INTERACTION_SUB_ID}/form"
)

TEST_FOOD_PREMISES_APPLY_FORM_URL = (
    f"/{SERVICE_SLUG}/{FOOD_PREMISES_APPLICATION_SLUG}/"
    f"{TEST_AUTH_SLUG}/{TEST_INTERACTION}-{TEST_INTERACTION_SUB_ID}/form"
)


@pytest.fixture(scope="session", autouse=True)
def django_db_setup():
    pass


TEST_LICENCE_CODE = "1234-5-6"


TEST_AUTHORITY = Authority(
    _id=ObjectId("50c8520393867870cb0d775f"),
    name="Test Authority",
    url_slug="test-authority",
    full_name="Test Authority for testing with",
    countries=[Countries.ENGLAND, Countries.WALES],
    licence_details=[
        LicenceDetails(
            licence_code=TEST_LICENCE_CODE,
            offered_by_authority=True,
            using_gov_uk=True,
            authority_url="https://test-authority.com",
        )
    ],
    contact_details=ContactDetails(),
)


TEST_TEMP_EVENT_LICENCE = Licence(
    _id=ObjectId("50c8520393867870cb0d775f"),
    name="Test Licence",
    licence_code=TEST_LICENCE_CODE,
    legislation_name=["Licensing Act 2003"],
    url_slug="test-licence",
    local_government_service_list_id=1234,
    administrative_area=AdministrativeArea(
        code="5", name=f"{Countries.ENGLAND},{Countries.WALES}", countries=[Countries.ENGLAND, Countries.WALES]
    ),
    is_offered_by_county=False,
    licence_interactions=[
        LicenceInteraction(
            interaction_id=0,
            interaction_sub_id=1,
            licence_interaction_name="Application for a Test Licence",
            form=LicenceForm(
                name="Test Licence Form",
                sub_form=1,
                form_ref_number="123000000",
                file_name="EAF_123000000_LA_TEST",
                file_size=185000,
                form_version=2,
            ),
            sub_forms=[],
            supporting_documents=[],
            fee=PaymentAmount(pence=2100),
            fee_calculation_instructions=[],
            tacit_consent="required",
        )
    ],
)

TEST_LICENCE_AUTH_AND_INTERACTION = LicenceAuthoritiesAndInteractionsResponse(
    is_offered_by_county=True,
    is_location_specific=True,
    geographical_availability=[Countries.ENGLAND],
    issuing_authorities=[
        IssuingAuthority(
            authority_name="Test Authority",
            authority_slug="test-authority",
            authority_contact=AuthorityContactDetails(
                website="https://test-authority.com",
                email="test@test-authority.com",
                phone="12345667801",
                address="Test Address",
            ),
            authority_interactions={
                "apply": [
                    AuthorityInteraction(
                        url="https://test-authority.com",
                        uses_authority_url=True,
                        uses_licensify=True,
                        description="Test description",
                        payment="Test payment",
                        introduction_text="Test introduction text",
                        payment_amount="optional",
                    )
                ]
            },
        )
    ],
)


@pytest.fixture
def mock_lookup_service(mocker):
    mock_look_up_service = mocker.MagicMock()
    mocker.patch(
        "citizen_frontend.api.find_a_licence_integration.LicenceLookupService", return_value=mock_look_up_service
    )
    yield mock_look_up_service
