import hashlib
from copy import deepcopy

from citizen_frontend.payment_providers.mock_providers.northgate.mock_requests import MOCK_REQUEST_NORTHGATE

MOCK_SUCCESS_RESPONSE_NORTHGATE = {
    "transactiontype": "B2",
    "amount": MOCK_REQUEST_NORTHGATE["amount"],
    "data": MOCK_REQUEST_NORTHGATE["data"],
    "merchantnumber": "random merchant number",
    "authorisationcode": "random authorization code",
    "receiptnumber": "random recipient number",
    "date": "a date",
    "merchantid": "random merchant ID",
    "serviceprocessed": "true",
    "administrationcharge": "0.00",
}

MOCK_NORTHGATE_FAILURE_RESPONSE = {
    "transactiontype": "B2",
    "data": MOCK_REQUEST_NORTHGATE["data"],
    "merchantid": "random merchant number",
    "date": "a date",
    "serviceprocessed": "false",
    "authorisationcode": "failed",
}

MOCK_NORTHGATE_CANCEL_RESPONSE = {
    "transactiontype": "B2",
    "data": MOCK_REQUEST_NORTHGATE["data"],
    "merchantid": "random merchant number",
    "date": "a date",
    "serviceprocessed": "false",
    "reason": "cancel",
}

MOCK_NORTHGATE_ERROR_RESPONSE = {
    "transactiontype": "B2",
    "data": MOCK_REQUEST_NORTHGATE["data"],
    "merchantid": "random merchant number",
    "date": "a date",
    "serviceprocessed": "false",
    "error": "there was an error",
}


def build_northgate_response_with_hash(response_dict):
    string_to_hash = ""
    for key, value in response_dict.items():
        string_to_hash += f"{key}={value}"
    string_to_hash += "sharedSecret"

    dict_to_return = deepcopy(response_dict)
    dict_to_return["hash"] = hashlib.sha256(string_to_hash.encode("utf-8")).hexdigest()

    return dict_to_return
