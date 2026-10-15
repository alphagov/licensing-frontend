import json
from copy import deepcopy

from django import forms


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
