from urllib.parse import urlencode

from django.http import JsonResponse
from django.shortcuts import redirect
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
def handle_success(request):
    callback_url = "http://" + request.get_host() + reverse("northgateCallback")

    request_form = NorthgateRequestForm(request.GET)
    if request_form.is_valid():
        params = build_response("success")
        encoded_params = urlencode(params)
        redirect_url = f"{callback_url}?{encoded_params}"
        redirect(to=redirect_url)

        return JsonResponse(f"success: redirected to {redirect_url}", safe=False)


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
