# TODO hash request? => we send both the xml request as a string and hash it using account secret as key
import base64
import hashlib
import hmac

from citizen_frontend.payment_providers.forms.access_paysuite import AccessPaysuiteRequestForm

with open("citizen_frontend/payment_providers/mock_providers/access_paysuite/request.xml", encoding="utf-8") as f:
    xml_string = f.read()


def hash_xml(string):
    signature = hmac.new(b"super_secret", msg=string, digestmod=hashlib.sha256).digest()

    return base64.b64encode(signature).decode("utf-8")


request = {
    "portal_id": "this is the merchant id from account",
    "hash": hash_xml(xml_string),
    "portalReq": xml_string,
    "schemaId": "APPXML_V2",
}


MOCK_ACCESS_PAYSUITE_REQUEST_FORM = AccessPaysuiteRequestForm(request)
