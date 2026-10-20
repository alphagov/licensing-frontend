from citizen_frontend.payment_providers.forms.access_paysuite import AccessPaymentProviderResponseForm
from citizen_frontend.payment_providers.mock_providers.access_paysuite.mock_requests import hash_xml

with open(
    "citizen_frontend/payment_providers/mock_providers/access_paysuite/mock_success_response.xml", encoding="utf-8"
) as f:
    success_xml_string = f.read()

success_response = {
    "status": success_xml_string,
    "hash": hash_xml(success_xml_string),
}

MOCK_ACCESS_PAYSUITE_SUCCESS_FORM = AccessPaymentProviderResponseForm(success_response)
