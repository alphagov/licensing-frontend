from urllib.parse import urlencode

from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from citizen_frontend.payment_providers.forms.access_paysuite import AccessPaysuiteRequestForm
from citizen_frontend.payment_providers.mock_providers.access_paysuite.mock_responses import (
    card_declined_response,
    known_failure_response,
    success_response,
    unknown_failure_response,
)


# current mock does redirects...?
@csrf_exempt
def handle_success(request):
    call_back_url = "http://" + request.get_host() + reverse("accessPaysuiteCallback")

    request_form = AccessPaysuiteRequestForm(request.POST)
    if request_form.is_valid():
        encoded_params = urlencode(success_response)
        redirect(to=f"{call_back_url}?{encoded_params}")

        return HttpResponse("success")


@csrf_exempt
def handle_known_failure(request):
    call_back_url = "http://" + request.get_host() + reverse("accessPaysuiteCallback")
    request_form = AccessPaysuiteRequestForm(request.POST)
    if request_form.is_valid():
        encoded_params = urlencode(known_failure_response)

        redirect(to=f"{call_back_url}?{encoded_params}")

        return HttpResponse("known failure")


@csrf_exempt
def handle_unknown_failure(request):
    call_back_url = "http://" + request.get_host() + reverse("accessPaysuiteCallback")
    request_form = AccessPaysuiteRequestForm(request.POST)

    if request_form.is_valid():
        encoded_params = urlencode(unknown_failure_response)
        redirect(to=f"{call_back_url}?{encoded_params}")

        return HttpResponse("unknown failure")


@csrf_exempt
def handle_card_declined(request):
    call_back_url = "http://" + request.get_host() + reverse("accessPaysuiteCallback")
    request_form = AccessPaysuiteRequestForm(request.POST)

    if request_form.is_valid():
        encoded_params = urlencode(card_declined_response)
        redirect(to=f"{call_back_url}?{encoded_params}")

        return HttpResponse("card declined")


def call_back(request):
    pass
