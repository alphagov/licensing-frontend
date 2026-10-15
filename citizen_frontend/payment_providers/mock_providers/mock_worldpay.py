import requests
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from citizen_frontend.payment_providers.forms.mock_forms import MockWorldPayRequestForm, MockWorldPayResponseForm


def create_response(data: dict):
    if data["cartId"] == "12345":
        return MockWorldPayResponseForm(
            {
                "cartId": data["cartId"],
                "instId": data["instId"],
                "amount": data["amount"],
                "transStatus": "Y",
                "transId": "UUID",
                "callBackPW": data["callBackPW"],
            }
        )


@require_POST
def handle_payment(request):
    callback_url = "http://" + request.get_host() + reverse("worldpayCallback")

    form_data = MockWorldPayRequestForm(request.POST)

    if form_data.is_valid():
        response_form = create_response(form_data.cleaned_data)

        if response_form.is_valid():
            requests.post(callback_url, data=response_form.cleaned_data)

    return JsonResponse(status=200, data={key: request.POST.getlist(key) for key in request.GET})
