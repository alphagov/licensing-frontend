import requests
from django.http import HttpResponse
from django.urls import reverse

from citizen_frontend.payment_providers.forms.access_paysuite import AccessPaysuiteRequestForm
from citizen_frontend.payment_providers.mock_providers.access_paysuite.mock_responses import (
    known_failure_response,
    success_response,
)


# current mock does redirects...?
def handle_success(request):
    call_back_url = "http://" + request.get_host() + reverse("accessPaysuiteCallback")

    request_form = AccessPaysuiteRequestForm(request.POST)
    if request_form.is_valid():
        requests.get(url=call_back_url, params=success_response)

        return HttpResponse("success")


def handle_known_failure(request):
    call_back_url = "http://" + request.get_host() + reverse("accessPaysuiteCallback")
    request_form = AccessPaysuiteRequestForm(request.POST)
    if request_form.is_valid():
        requests.get(url=call_back_url, params=known_failure_response)

        return HttpResponse("success")


def call_back(request):
    pass
