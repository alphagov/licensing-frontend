import os

import pytest
from bson import ObjectId
from common.models.licences import AdministrativeArea, Licence, LicenceForm, LicenceInteraction
from common.models.shared_models import PaymentAmount

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


TEST_TEMP_EVENT_LICENCE = Licence(
    _id=ObjectId("50c8520393867870cb0d775f"),
    name="Test Licence",
    licence_code="1234-5-6",
    legislation_name=["Licensing Act 2003"],
    url_slug="test-licence",
    local_government_service_list_id=1234,
    administrative_area=AdministrativeArea(code="5", name="England,Wales", countries=["England", "Wales"]),
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

# TEST_TEMP_EVENT_LICENCE = {
#     "_id": "50c8520393867870cb0d775f",
#     "name": "Test Licence",
#     "licenceCode": "1234-5-6",
#     "legislationName": ["Licensing Act 2003"],
#     "urlSlug": "test-licence",
#     "lgslId": 1234,
#     "administrativeArea": {"code": "5", "name": "England,Wales", "countries": ["England", "Wales"]},
#     "interactions": [
#         {
#             "lgilId": 0,
#             "lgilSubId": 1,
#             "licenceInteractionName": "Application for a Test Licence",
#             "form": {
#                 "name": "Test Licence Form",
#                 "subForm": 1,
#                 "formRefNo": "123000000",
#                 "fileName": "EAF_123000000_LA_TEST",
#                 "fileSizeInBytes": 185000,
#                 "formVersion": 2,
#             },
#             "subForms": [],
#             "supportingDocuments": [],
#             "fee": {"pence": 2100},
#             "feeCalculationInstructions": [],
#             "tacitConsent": "required",
#         }
#     ],
# }
