from common.models.authority import Authority
from common.models.interaction_customisation import Customisation
from common.models.payment import Payment
from common.models.shared_models import PaymentAmount
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.cache import never_cache

import citizen_frontend.services.licence_lookup_service as licence_lookup_service
from citizen_frontend.repository.licence_application_repository import LicenceApplicationRepository


@never_cache
def application_uploaded(request):

    application_ref = request.GET.get("id")

    if application_ref is None:
        raise Http404("No application id provided")

    application_refs = request.session.get("applicationReferenceNumbers", [])
    if application_ref not in application_refs:
        raise Http404("Application id not in session")

    application, customisation = get_details(application_ref)

    if customisation.is_fee_required:
        if application.required_payment_amount is None:
            context = mock_provide_fee_context()
            return render(request, "citizen_frontend/licence_application_provide_fee_amount_page.html", context)
        if application.required_payment_amount.pence > 0:
            context = mock_prepayment_context()
            return render(request, "citizen_frontend/licence_application_prepayment_page.html", context)
    else:
        context = mock_no_fee_context()
        return render(request, "citizen_frontend/licence_submission_success_page.html", context)


def get_details(application_ref):
    application_repo = LicenceApplicationRepository()
    application = application_repo.get_application_from_id(application_ref)
    licence, authority, interaction, _ = licence_lookup_service.get_licence_interaction_context(
        application.authority, application.licence, application.service.interaction_id, application.service.interaction_sub_id
    )
    customisation = Customisation(is_fee_required=False)
    return application, customisation


def mock_no_fee_context():
    pass


def mock_provide_fee_context():
    pass

def mock_prepayment_context():
    authority = Authority(name="Test Authority", full_name="Test Authority for testing with")
    payment = Payment(amount=PaymentAmount(pence=500), payment_provider="WorldPay")
    published_customisation = Customisation(is_fee_required=True)

    return {
        "licence_name": "Test Licence",
        "authority": authority,
        "payment": payment,
        "published_customisation": published_customisation,
        "step": "3",
    }
