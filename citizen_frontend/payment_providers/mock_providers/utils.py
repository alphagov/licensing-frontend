import base64
import hashlib
import hmac
from xml.etree import ElementTree as ET


def hash_xml(string):
    signature = hmac.new(b"super_secret", msg=string.encode("utf-8"), digestmod=hashlib.sha256).digest()

    return base64.b64encode(signature).decode("utf-8")


def single_line_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()
    return ET.tostring(root, encoding="utf-8", method="xml").decode("utf-8")
