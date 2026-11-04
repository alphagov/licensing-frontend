from common.models.authority import Authority
from common.models.department import Department
from django.shortcuts import render


def payment_licence_callback(request):
    context = mock_payment_licence_callback_context()
    return render(request, "citizen_frontend/licence_submission_sucess_page.html", context)


def payment_licence_callback_cancelled(request):
    context = mock_payment_licence_callback_cancelled_context()
    return render(request, "citizen_frontend/licence_submission_cancelled_page.html", context)


def mock_payment_licence_callback_cancelled_context():
    pass


def mock_payment_licence_callback_context():
    department = Department(
        authority_slug="TEST_AUTHORITY.url_slug",
        name="Test Department",
        helpline_phone_number="TEST_AUTHORITY.contact_details.phone_number",
        helpline_email_address="TEST_AUTHORITY.contact_details.email",
        address_line_1="TEST_AUTHORITY.contact_details.line_one",
        address_line_2="TEST_AUTHORITY.contact_details.line_two",
        address_line_3="TEST_AUTHORITY.contact_details.line_three",
        address_line_4="TEST_AUTHORITY.contact_details.city",
        postcode="TEST_AUTHORITY.contact_details.post_code",
        notification_email_address="notify@email.com",
        default_privacy_notice_url="test-privacy-notice-url",
    )
    authority = Authority(
        name="Test Authority",
    )
    return {
        "licence_name": "Test Licence",
        "authority": authority,
        "step": "4",
        "steps": "4",
        "fee_required": True,
        "is_paid": True,
        "applicant_email": "test@email.com",
        "transaction_id": "transaction_id",
        "transaction_id_exists": True,
        "payment_provider_exists": True,
        "payment_provider": "WorldPay",
        "application_reference_number": "123456",
        "application_has_supporting_documents_online": False,
        "all_supporting_documents_required": False,
        "has_supporting_documents": True,
        "has_expected_processing_date": True,
        "expected_processing_date": "06 November 2026",
        "application_has_tacit_consent": False,
        "authority_full_name": "Test Authority",
        "processing_days": "30 working days",
        "department": department,
        "licence_finder_url": "localhost:8000/apply-for-a-licence",
    }
