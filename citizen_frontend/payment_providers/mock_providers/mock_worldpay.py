import requests
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from citizen_frontend.payment_providers.forms.mock_forms import MockWorldPayRequestForm, MockWorldPayResponseForm


def create_response(data: dict):
    mock_response = {
        "cartId": data["cartId"],
        "instId": data["instId"],
        "amount": data["amount"],
        "transId": "UUID",
        "callBackPW": data["callBackPW"],
        "transStatus": "Y",
    }
    if data["cartId"] == "12345":
        mock_response["transStatus"] = "Y"
    if data["cartId"] == "67890":
        # "C" represents a failed payment, no transID is included in a failed response
        mock_response["transStatus"] = "C"
        mock_response.pop("transId")

    return MockWorldPayResponseForm(mock_response)


@require_POST
def handle_payment(request):
    callback_url = "http://" + request.get_host() + reverse("worldpayCallback")

    form_data = MockWorldPayRequestForm(request.POST)

    if form_data.is_valid():
        response_form = create_response(form_data.cleaned_data)

        if response_form.is_valid():
            requests.post(callback_url, data=response_form.cleaned_data)

        return JsonResponse(status=200, data={})

    else:
        return JsonResponse(status=400, data="Invalid request", safe=False)
