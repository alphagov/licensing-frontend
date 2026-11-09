from common.models.authority import Authority
from common.models.department import Department
from common.models.licence import Licence
from django.shortcuts import render


def payment_licence_callback(request):
    payment_status = mock_payment_response_status()
    context = mock_payment_licence_callback_context()
    if payment_status == "cancelled":
        return render(request, "citizen_frontend/licence_submission_cancelled_page.html", context)
    else:
        return render(request, "citizen_frontend/licence_submission_sucess_page.html", context)


def mock_payment_response_status():
    return ""


def mock_payment_licence_callback_context():
    department = Department(
        authority_slug="test-authority",
        name="Test Department",
        helpline_phone_number="01234 567 890",
        helpline_email_address="TEST_AUTHORITY.contact_details.email",
        address_line_1="A building",
        address_line_2="A street",
        address_line_3="A line three",
        address_line_4="London",
        postcode="a12 21a",
        notification_email_address="notify@email.com",
        default_privacy_notice_url="test-privacy-notice-url",
    )
    authority = Authority(
        name="Test Authority",
        full_name="Test Authority Full Name",
    )
    licence = Licence(
        name="Test Licence",
    )
    return {
        "licence_name": "Test Licence",
        "licence": licence,
        "authority": authority,
        "step": "4",
        # "fee_required": True,
        # "is_paid": True,
        # "applicant_email": "test@email.com",
        # "transaction_id": "transaction_id",
        # "transaction_id_exists": True,
        # "payment_provider_exists": True,
        # "payment_provider": "WorldPay",
        # "application_reference_number": "123456",
        # "application_has_supporting_documents_online": False,
        # "all_supporting_documents_required": False,
        # "has_supporting_documents": True,
        # "has_expected_processing_date": True,
        # "expected_processing_date": "06 November 2026",
        # "application_has_tacit_consent": False,
        # "authority_full_name": "Test Authority",
        # "processing_days": "30 working days",
        "department": department,
        "licence_finder_url": "localhost:8000/apply-for-a-licence",
    }
