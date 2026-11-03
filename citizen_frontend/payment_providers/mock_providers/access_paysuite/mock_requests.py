from citizen_frontend.payment_providers.forms.access_paysuite import AccessPaysuiteRequestForm
from citizen_frontend.payment_providers.mock_providers.utils import hash_xml, single_line_xml

xml_string = single_line_xml("citizen_frontend/payment_providers/mock_providers/access_paysuite/request.xml")

mock_access_paysuite_request = {
    "portal_id": "this is the merchant id from account",
    "hash": hash_xml(xml_string),
    "portalReq": xml_string,
    "schemaId": "APPXML_V2",
}


MOCK_ACCESS_PAYSUITE_REQUEST_FORM = AccessPaysuiteRequestForm(mock_access_paysuite_request)
