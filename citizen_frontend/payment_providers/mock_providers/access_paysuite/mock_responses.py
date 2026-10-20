from citizen_frontend.payment_providers.mock_providers.utils import hash_xml, single_line_xml

success_xml_string = single_line_xml(
    "citizen_frontend/payment_providers/mock_providers/access_paysuite/mock_success_response.xml"
)

success_response = {
    "hash": hash_xml(success_xml_string),
    "status": success_xml_string,
}

known_failure_xml_string = single_line_xml(
    "citizen_frontend/payment_providers/mock_providers/access_paysuite/mock_known_failure_response.xml"
)

known_failure_response = {
    "hash": hash_xml(known_failure_xml_string),
    "status": known_failure_xml_string,
}

unknown_failure_xml_string = single_line_xml(
    "citizen_frontend/payment_providers/mock_providers/access_paysuite/mock_unknow_failure_response.xml"
)

unknown_failure_response = {
    "hash": hash_xml(unknown_failure_xml_string),
    "status": unknown_failure_xml_string,
}

card_decline_xml_string = single_line_xml(
    "citizen_frontend/payment_providers/mock_providers/access_paysuite/mock_card_declined.xml"
)

card_declined_response = {
    "hash": hash_xml(card_decline_xml_string),
    "status": card_decline_xml_string,
}
