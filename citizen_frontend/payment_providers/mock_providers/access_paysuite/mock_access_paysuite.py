import requests
from django.http import HttpResponse
from django.urls import reverse


def handle_success(request):
    call_back_url = "http://" + request.get_host() + reverse("accessPaysuiteCallback")
    requests.get(url=call_back_url)

    return HttpResponse("success")


def call_back(request):
    pass
