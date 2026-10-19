import xml.etree.ElementTree as ET

import requests
from django.http import JsonResponse
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


@require_GET
def handle_payment(request):
    request_form = NorthgateRequestForm(request.GET)

    if request_form.is_valid():
        params = build_response(request_form.cleaned_data)
        requests.get(url=request_form.cleaned_data["returnurl"], params=params)

        return JsonResponse(status=200, data=params)


def build_response(request: dict) -> dict:
    outcome_response_map = {
        "success": MOCK_SUCCESS_RESPONSE_NORTHGATE,
        "failure": MOCK_NORTHGATE_FAILURE_RESPONSE,
        "cancel": MOCK_NORTHGATE_CANCEL_RESPONSE,
        "error": MOCK_NORTHGATE_ERROR_RESPONSE,
    }

    xml_record_root = ET.fromstring(request.get("recordxml", ""))
    outcome = xml_record_root.findtext(".//reference")

    response_form = NorthgateResponseForm(build_northgate_response_with_hash(outcome_response_map.get(outcome)))
    if response_form.is_valid():
        return response_form.cleaned_data


def callback(request):
    return JsonResponse(status=200, data={})
