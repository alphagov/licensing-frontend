from django.shortcuts import render

from common.models.authority import Authority
from common.models.interaction_customisation import Customisation
from common.models.payment import Payment
from common.models.shared_models import PaymentAmount
from django.http import Http404


def application_uploaded(request):

    application_ref = request.GET.get("id")

    if application_ref is None:
        raise Http404("No application id provided")

    application_refs = request.session.get("applicationReferenceNumbers", [])
    if application_ref not in application_refs:
        raise Http404("Application id not in session")

    context = mock_no_fee_context()
    return render(request, "citizen_frontend/licence_submission_success_page.html", context)



def get_details(application_ref):
    pass


def mock_no_fee_context():
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
