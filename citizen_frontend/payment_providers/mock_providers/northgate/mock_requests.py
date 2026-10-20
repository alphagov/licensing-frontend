from copy import deepcopy

from citizen_frontend.payment_providers.mock_providers.utils import single_line_xml

success_record = single_line_xml("citizen_frontend/payment_providers/mock_providers/northgate/mock_success_record.xml")

MOCK_SUCCESS_REQUEST_NORTHGATE = {
    "data": "we send this and then expect it back",
    "returnurl": "http://testserver/fake/payment/northgateCallback",
    "returntext": "take me back",
    "amount": "10.00",
    "recordxml": success_record,
    "payforbasketmode": "true",
    "ignoreconfirmation": "true",
}


failure_record = single_line_xml("citizen_frontend/payment_providers/mock_providers/northgate/mock_failure_record.xml")

MOCK_NORTHGATE_FAILURE_REQUEST = deepcopy(MOCK_SUCCESS_REQUEST_NORTHGATE)
MOCK_NORTHGATE_FAILURE_REQUEST["recordxml"] = failure_record

cancel_record = single_line_xml("citizen_frontend/payment_providers/mock_providers/northgate/mock_cancel_record.xml")

MOCK_NORTHGATE_CANCEL_REQUEST = deepcopy(MOCK_SUCCESS_REQUEST_NORTHGATE)
MOCK_NORTHGATE_CANCEL_REQUEST["recordxml"] = cancel_record

error_record = single_line_xml("citizen_frontend/payment_providers/mock_providers/northgate/mock_error_record.xml")

MOCK_NORTHGATE_ERROR_REQUEST = deepcopy(MOCK_SUCCESS_REQUEST_NORTHGATE)
MOCK_NORTHGATE_ERROR_REQUEST["recordxml"] = error_record
