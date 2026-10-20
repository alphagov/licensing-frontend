import xml.etree.ElementTree as ET

from citizen_frontend.payment_providers.forms.access_paysuite import AccessPaymentProviderResponseForm
from citizen_frontend.payment_providers.mock_providers.access_paysuite.mock_requests import hash_xml


def single_line_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    return ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")


success_xml_string = single_line_xml(
    "citizen_frontend/payment_providers/mock_providers/access_paysuite/mock_success_response.xml"
)

success_response = {
    "status": success_xml_string,
    "hash": hash_xml(success_xml_string),
}

known_failure_xml_string = single_line_xml(
    "citizen_frontend/payment_providers/mock_providers/access_paysuite/mock_failure_response.xml"
)

known_failure_response = {
    "status": known_failure_xml_string,
    "hash": hash_xml(known_failure_xml_string),
}

MOCK_ACCESS_PAYSUITE_SUCCESS_FORM = AccessPaymentProviderResponseForm(success_response)
MOCK_ACCESS_PAYSUITE_KNOWN_FAILURE_FORM = AccessPaymentProviderResponseForm(known_failure_response)
