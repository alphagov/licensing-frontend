from urllib.parse import urlencode

from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from citizen_frontend.payment_providers.forms.mock_forms import (
    NorthgateRequestForm,
    NorthgateResponseForm,
)
from citizen_frontend.payment_providers.mock_providers.northgate.mock_responses import (
    MOCK_NORTHGATE_CANCEL_RESPONSE,
    MOCK_NORTHGATE_ERROR_RESPONSE,
    MOCK_NORTHGATE_FAILURE_RESPONSE,
    MOCK_SUCCESS_RESPONSE_NORTHGATE,
    build_northgate_response_with_hash,
)


@csrf_exempt
@require_GET
def handle_payment(request):
    callback_url = "http://" + request.get_host() + reverse("northgateCallback")
    scenario = request.path.split("-")[1]

    request_form = NorthgateRequestForm(request.GET)
    if request_form.is_valid():
        params = build_response(scenario)
        encoded_params = urlencode(params)
        redirect_url = f"{callback_url}?{encoded_params}"

        return HttpResponseRedirect(redirect_url)


def build_response(outcome: str) -> dict:
    outcome_response_map = {
        "success": MOCK_SUCCESS_RESPONSE_NORTHGATE,
        "failure": MOCK_NORTHGATE_FAILURE_RESPONSE,
        "cancel": MOCK_NORTHGATE_CANCEL_RESPONSE,
        "error": MOCK_NORTHGATE_ERROR_RESPONSE,
    }

    response_form = NorthgateResponseForm(build_northgate_response_with_hash(outcome_response_map.get(outcome)))
    if response_form.is_valid():
        return response_form.cleaned_data


def callback(request):
    return JsonResponse(status=200, data={})
