from urllib.parse import urlencode

from django.http import HttpResponseRedirect
from django.urls import reverse

from citizen_frontend.payment_providers.forms.civica import CivicaRequestForm
from citizen_frontend.payment_providers.mock_providers.civica.mock_responses import mock_success_response


def handle_payment(request):
    call_back_url = "http://" + request.get_host() + reverse("civicaCallback")
    scenario = request.path.split("-")[1]

    request_form = CivicaRequestForm(request.POST)

    responses = {
        "success": mock_success_response,
    }

    if request_form.is_valid():
        encoded_params = urlencode(responses.get(scenario))
        return HttpResponseRedirect(f"{call_back_url}?{encoded_params}")


def callback(request):
    pass
