from citizen_frontend.payment_providers.mock_providers.utils import single_line_xml

record = single_line_xml("citizen_frontend/payment_providers/mock_providers/northgate/mock_record.xml")

MOCK_REQUEST_NORTHGATE = {
    "data": "we send this and then expect it back",
    "returnurl": "http://testserver/fake/payment/northgateCallback",
    "returntext": "take me back",
    "amount": "10.00",
    "recordxml": record,
    "payforbasketmode": "true",
    "ignoreconfirmation": "true",
}
