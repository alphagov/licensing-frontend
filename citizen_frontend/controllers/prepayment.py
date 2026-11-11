from common.models.authority import Authority
from django.shortcuts import render


def prepayment(request):
    context = mock_prepayment_context()
    return render(request, "citizen_frontend/licence_application_prepayment_page.html", context)


def mock_prepayment_context():
    authority = Authority(name="Test Authority", full_name="Test Authority Full Name")
    return {"licence_name": "Test Licence", "authority": authority}
