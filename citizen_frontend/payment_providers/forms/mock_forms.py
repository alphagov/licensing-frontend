import hashlib
import json
from copy import deepcopy

from django import forms

"""
WORLDPAY
"""


# TODO check data structure of acctId
class MockWorldPayRequestForm(forms.Form):
    cartId = forms.CharField()
    callBackPW = forms.CharField()
    amount = forms.CharField()
    currency = forms.CharField()
    signature = forms.CharField()
    desc = forms.CharField()
    authValidTo = forms.CharField()
    acctId = forms.JSONField()
    instId = forms.CharField()


class MockWorldPayResponseForm(forms.Form):
    cartId = forms.CharField()
    instId = forms.CharField()
    amount = forms.CharField()
    callBackPW = forms.CharField()
    transStatus = forms.CharField()
    transId = forms.CharField(required=False)


# unsure of data structure of acctId
SUCCESSFUL_PAYMENT_REQUEST = {
    "cartId": "12345",
    "callBackPW": "supersecret",
    "amount": "10",
    "currency": "GBP",
    "signature": "MD5 signature created from various variables",
    "desc": "description or purchase code",
    "authValidTo": "string time tha auth is valid to",
    "acctId": json.dumps({"details": "from", "payment": "parameters"}),
    "instId": "merchant id on payment account",
}

FAILED_PAYMENT_REQUEST = deepcopy(SUCCESSFUL_PAYMENT_REQUEST)
FAILED_PAYMENT_REQUEST["cartId"] = "67890"

NON_MATCHING_PASSWORD_PAYMENT_REQUEST = deepcopy(SUCCESSFUL_PAYMENT_REQUEST)
NON_MATCHING_PASSWORD_PAYMENT_REQUEST["cartId"] = "11111"
NON_MATCHING_PASSWORD_PAYMENT_REQUEST["callBackPW"] = "not matching"
NON_MATCHING_PASSWORD_PAYMENT_REQUEST["signature"] = "not matching"

SUCCESS_REQUEST_FORM = MockWorldPayRequestForm(SUCCESSFUL_PAYMENT_REQUEST)
FAILED_REQUEST_FORM = MockWorldPayRequestForm(FAILED_PAYMENT_REQUEST)
NON_MATCHING_REQUEST_FORM = MockWorldPayRequestForm(NON_MATCHING_PASSWORD_PAYMENT_REQUEST)


"""
NORTHGATE
"""


# Do we need to use forms in this instance?
# Yes it's an easy way to bind and validate querystring params on a GET request.
class MockNorthgateRequestForm(forms.Form):
    amount = forms.CharField()
    returnurl = forms.CharField()
    returntext = forms.CharField()
    ignoreconfirmation = forms.CharField(initial="true")
    data = forms.CharField()
    payforbasketmode = forms.CharField(initial="true")
    recordxml = forms.CharField()


class MockNorthgateResponseForm(forms.Form):
    transactiontype = forms.CharField(required=False)
    amount = forms.CharField(required=False)
    administrationcharge = forms.CharField(required=False)
    data = forms.CharField()
    merchantnumber = forms.CharField(required=False)
    authorisationcode = forms.CharField(required=False)
    date = forms.CharField(required=False)
    merchanttid = forms.CharField(required=False)
    serviceprocessed = forms.CharField()
    receiptnumber = forms.CharField(required=False)
    hash = forms.CharField()
    authorisationstatus = forms.CharField(required=False)
    reason = forms.CharField(required=False)
    error = forms.CharField(required=False)


# how often does this happen if this is here? once?, alot?
with open("citizen_frontend/payment_providers/mock_providers/mock_success_record.xml", encoding="utf-8") as f:
    success_record = f.read()

MOCK_SUCCESS_REQUEST_NORTHGATE = {
    "data": "we send this and then expect it back",
    "returnurl": "http://testserver/fake/payment/northgateCallback",
    "returntext": "take me back",
    "amount": "10.00",
    "recordxml": success_record,
    "payforbasketmode": "true",
    "ignoreconfirmation": "true",
}

MOCK_SUCCESS_RESPONSE_NORHTGATE = {
    "transactiontype": "B2",
    "amount": MOCK_SUCCESS_REQUEST_NORTHGATE["amount"],
    "data": MOCK_SUCCESS_REQUEST_NORTHGATE["data"],
    "merchantnumber": "random merchant number",
    "authorisationcode": "random authorization code",
    "recipientnumber": "random recipient number",
    "date": "a date",
    "merchanttid": "random merchant ID",
    "serviceprocessed": "true",
    "administrationcharge": "0.00",
}

with open("citizen_frontend/payment_providers/mock_providers/mock_failure_record.xml", encoding="utf-8") as f:
    failure_record = f.read()


MOCK_NORTHGATE_FAILURE_REQUEST = {
    "data": "we send this and then expect it back",
    "returnurl": "http://testserver/fake/payment/northgateCallback",
    "returntext": "take me back",
    "amount": "10.00",
    "recordxml": failure_record,
    "payforbasketmode": "true",
    "ignoreconfirmation": "true",
}

MOCK_NORTHGATE_FAILURE_RESPONSE = {
    "transactiontype": "B2",
    "data": MOCK_SUCCESS_REQUEST_NORTHGATE["data"],
    "merchantid": "random merchant number",
    "date": "a date",
    "serviceprocessed": "false",
    "authorisationcode": "failed",
}


def build_northgate_response_with_hash(response_dict):
    string_to_hash = ""
    for key, value in response_dict.items():
        string_to_hash += f"{key}={value}"
    string_to_hash += "sharedSecret"

    dict_to_return = deepcopy(response_dict)
    dict_to_return["hash"] = hashlib.sha256(string_to_hash.encode("utf-8")).hexdigest()

    return dict_to_return


MOCK_NORTHGATE_RESPONSE_SUCCESS_FORM = MockNorthgateResponseForm(MOCK_SUCCESS_REQUEST_NORTHGATE)
