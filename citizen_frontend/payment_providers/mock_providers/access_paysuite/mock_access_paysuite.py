from urllib.parse import urlencode

from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from citizen_frontend.payment_providers.forms.access_paysuite import AccessPaysuiteRequestForm
from citizen_frontend.payment_providers.mock_providers.access_paysuite.mock_responses import (
    card_declined_response,
    known_failure_response,
    success_response,
    unknown_failure_response,
)


@csrf_exempt
def handle_payment(request):
    call_back_url = "http://" + request.get_host() + reverse("accessPaysuiteCallback")
    request_form = AccessPaysuiteRequestForm(request.POST)

    scenario = request.path.split("/")[-1].replace("access-paysuite-", "")

    responses = {
        "success": success_response,
        "known-failure": known_failure_response,
        "card-declined": card_declined_response,
        "unknown-failure": unknown_failure_response,
    }

    if request_form.is_valid():
        encoded_params = urlencode(responses.get(scenario, ""))
        return HttpResponseRedirect(f"{call_back_url}?{encoded_params}")

    return JsonResponse(status=400, data="Invalid request", safe=False)


def call_back(request):
    pass
