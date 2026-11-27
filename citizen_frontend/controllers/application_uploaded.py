from common.models.authority import Authority
from common.models.interaction_customisation import Customisation
from common.models.licence import Licence
from common.models.licence_application import LicenceApplication
from common.models.payment import Payment
from common.models.shared_models import PaymentAmount
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.cache import never_cache

import citizen_frontend.repository.interaction_customisation_repository as interaction_customisation_repository
import citizen_frontend.services.licence_lookup_service as licence_lookup_service
from citizen_frontend.repository.department_repository import DepartmentRepository
from citizen_frontend.repository.licence_application_repository import LicenceApplicationRepository
from citizen_frontend.repository.payment_repository import PaymentRepository


@never_cache
def application_uploaded(request):

    application_ref = request.GET.get("id")

    if application_ref is None:
        raise Http404("No application id provided")

    application_refs = request.session.get("applicationReferenceNumbers", [])
    if application_ref not in application_refs:
        raise Http404("Application id not in session")

    application, licence, authority, interaction, customisation = get_details(application_ref)
    if customisation is None:
        raise Http404("No customisation found")

    if not customisation.is_fee_required:
        context = licence_submission_success_page(application, licence, authority, customisation)
        return render(request, "citizen_frontend/licence_submission_success_page.html", context)

    if application.required_payment_amount and application.required_payment_amount.pence > 0:
        payment = create_payment(licence, customisation, application)
        context = licence_prepayment_page(licence, authority, customisation, payment)
        return render(request, "citizen_frontend/licence_application_prepayment_page.html", context)
    else:
        context = mock_provide_fee_context()
        return render(request, "citizen_frontend/licence_application_provide_fee_amount_page.html", context)


def get_details(application_ref):
    application_repo = LicenceApplicationRepository()
    application = application_repo.get_application_from_id(application_ref)
    licence, authority, interaction, _ = licence_lookup_service.get_licence_interaction_context(
        application.authority,
        application.licence,
        application.service.interaction_id,
        application.service.interaction_sub_id,
    )
    customisation = interaction_customisation_repository.find_published_customisation(
        application.authority,
        application.service.licence_code,
        application.service.interaction_id,
        application.service.interaction_sub_id,
    )
    return application, licence, authority, interaction, customisation


def licence_prepayment_page(licence: Licence, authority: Authority, customisation: Customisation, payment: Payment):
    return {
        "licence_name": licence.name,
        "authority": authority,
        "payment": payment,
        "published_customisation": customisation,
        "step": "3",
    }


def licence_submission_success_page(
    application: LicenceApplication, licence: Licence, authority, customisation: Customisation
):
    has_supporting_documents = customisation.supporting_document_definitions
    all_supporting_documents_required = (
        has_supporting_documents and customisation.all_supporting_documents_are_mandatory
    )
    processing_days = customisation.format_processing_days
    department = get_department(authority)

    context = {
        "licence_name": licence.name,
        "authority": authority,
        "published_customisation": customisation,
        "application": application,
        "has_supporting_documents": has_supporting_documents,
        "all_supporting_documents_required": all_supporting_documents_required,
        "processing_days": processing_days,
        "is_paid": False,
        "department": department,
        "step": "4" if customisation.is_fee_required else "3",
    }
    if application.expected_processing_date:
        formatted_expected_processing_date = application.expected_processing_date.strftime("%d %B %Y")
        context.update(
            {
                "expected_processing_date": formatted_expected_processing_date,
            }
        )
    return context


def create_payment(licence: Licence, customisation: Customisation, application: LicenceApplication):
    payment_repo = PaymentRepository()
    payment = payment_repo.create_new_payment(licence, customisation, application)
    return payment


def get_department(authority: Authority):
    department_repo = DepartmentRepository()
    department = department_repo.get_department_from_authority_slug(authority.url_slug)
    return department


def mock_provide_fee_context():
    pass


def mock_prepayment_context():
    authority = Authority(name="Test Authority", full_name="Test Authority Full Name")
    payment = Payment(amount=PaymentAmount(pence=500), payment_provider="WorldPay")
    published_customisation = Customisation(is_fee_required=True)

    return {
        "licence_name": "Test Licence",
        "authority": authority,
        "payment": payment,
        "published_customisation": published_customisation,
        "step": "3",
    }


# def mock_no_fee_context_for_local_render():
#     authority = Authority(name="Test Authority", full_name="Test Authority Full Name")
#     customisation = Customisation(
#         is_fee_required=False,
#         number_of_days_to_process=3,
#     )
#     application = LicenceApplication(
#         applicant_email="test@email.com",
#         application_reference_number="TestApplicationRef",
#         authority=authority.full_name,
#         has_supporting_documents_online=True,
#         expected_processing_date=now() + timedelta(days=7),
#         has_tacit_consent=True,
#     )
#     licence = Licence(name="Test Licence")
#     department = Department(
#         authority_slug="test-authority",
#         name="Test Department",
#         helpline_phone_number="01234 567 890",
#         helpline_email_address="department@email.com",
#         address_line_1="A building",
#         address_line_2="A street",
#         address_line_3="A line three",
#         address_line_4="London",
#         postcode="A12 21A",
#         notification_email_address="notify@email.com",
#         default_privacy_notice_url="test-privacy-notice-url"
#     )
