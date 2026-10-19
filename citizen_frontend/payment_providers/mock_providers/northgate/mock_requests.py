from copy import deepcopy

with open("citizen_frontend/payment_providers/mock_providers/northgate/mock_success_record.xml", encoding="utf-8") as f:
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

with open("citizen_frontend/payment_providers/mock_providers/northgate/mock_failure_record.xml", encoding="utf-8") as f:
    failure_record = f.read()

MOCK_NORTHGATE_FAILURE_REQUEST = deepcopy(MOCK_SUCCESS_REQUEST_NORTHGATE)
MOCK_NORTHGATE_FAILURE_REQUEST["recordxml"] = failure_record

with open("citizen_frontend/payment_providers/mock_providers/northgate/mock_cancel_record.xml", encoding="utf-8") as f:
    cancel_record = f.read()

MOCK_NORTHGATE_CANCEL_REQUEST = deepcopy(MOCK_SUCCESS_REQUEST_NORTHGATE)
MOCK_NORTHGATE_CANCEL_REQUEST["recordxml"] = cancel_record

with open("citizen_frontend/payment_providers/mock_providers/northgate/mock_error_record.xml", encoding="utf-8") as f:
    error_record = f.read()


MOCK_NORTHGATE_ERROR_REQUEST = deepcopy(MOCK_SUCCESS_REQUEST_NORTHGATE)
MOCK_NORTHGATE_ERROR_REQUEST["recordxml"] = error_record
