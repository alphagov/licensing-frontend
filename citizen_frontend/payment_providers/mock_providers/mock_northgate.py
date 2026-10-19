# / *
# An example call to Northgate:
#
# http://86.188.207.173/licensing/sales/launchinternet.aspx?returnurl=http://google.co.uk/&returntext=takemeback
# &ignoreconfirmation=true&data=keep this and return it at the end&payforbasketmode=true
# &recordxml=<records><record><fund>07</fund><reference>1274-722/9214</reference><amount>10</amount><memo>Test
# Eform license</memo><notes>ELMSUnique123123</notes></record></records>
#
# An example callback from Northgate
#
# http://callback.co.uk /?transactiontype=B2&amount=10.00&administrationcharge=0.00&
# data=keep%20this%20and%20return%20it%20at%20the%20end&merchantnumber=79807901&authorisationcode=13623
# &date=22%2F08%2F20122015 % 3
# A44 % 3
# A37
# &merchanttid=03089876&serviceprocessed=true
# &receiptnumber=VOS09 % 2
# F000167
# & hash = E8 - 14 - 15 - 19 - 76 - 19 - 6
# B - 61 - B1 - 51 - 7
# A - 61 - 80 - 10 - 06 - 71 - BD - DB - D8 - 0
# F - 3
# D - CB - AA - 61 - 85 - 95 - 5
# F - 99 - E8 - 5
# A - D0 - B1 - E3 - 02 - 20 - 95 - 22 - 6
# E - DB - 3E-4
# B - F0 - A3 - 3
# B - D6 - F1 - 8
# B - C0 - 07 - B3 - A4 - 3
# C - 0
# D - 0
# C - 14 - 25 - 32 - FA - 5
# F - A8 - BB - D3 - E0 - C1
# * /
import xml.etree.ElementTree as ET

import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from citizen_frontend.payment_providers.forms.mock_forms import (
    MOCK_NORTHGATE_FAILURE_RESPONSE,
    MOCK_SUCCESS_RESPONSE_NORHTGATE,
    MockNorthgateRequestForm,
    MockNorthgateResponseForm,
    build_northgate_response_with_hash,
)


@require_GET
def handle_payment(request):
    # callback = "http://" + request.get_host() + reverse("northgateCallback")

    request_form = MockNorthgateRequestForm(request.GET)

    if request_form.is_valid():
        params = build_response(request_form.cleaned_data)
        requests.get(url=request_form.cleaned_data["returnurl"], params=params)

    return JsonResponse(status=200, data={})


def build_response(request: dict) -> dict:
    outcome_response_map = {"success": MOCK_SUCCESS_RESPONSE_NORHTGATE, "failure": MOCK_NORTHGATE_FAILURE_RESPONSE}

    xml_record_root = ET.fromstring(request.get("recordxml", ""))
    outcome = xml_record_root.findtext(".//reference")

    response_form = MockNorthgateResponseForm(build_northgate_response_with_hash(outcome_response_map.get(outcome)))
    if response_form.is_valid():
        return response_form.cleaned_data


def callback(request):
    return JsonResponse(status=200, data={})
