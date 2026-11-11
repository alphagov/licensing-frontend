from common.models.authority import Authority
from common.models.payment import Payment
from common.models.interaction_customisation import Customisation
from common.models.shared_models import PaymentAmount
from django.shortcuts import render


def prepayment(request):
    context = mock_prepayment_context()
    return render(request, "citizen_frontend/licence_application_prepayment_page.html", context)


def mock_prepayment_context():
    authority = Authority(name="Test Authority", full_name="Test Authority Full Name")
    payment = Payment(amount=PaymentAmount(pence=500), payment_provider="WorldPay")
    published_customisation = Customisation(is_fee_required=True)

    return {
        "licence_name": "Test Licence",
        "authority": authority, "payment": payment,
        "published_customisation": published_customisation,
        "step": "3"
    }
