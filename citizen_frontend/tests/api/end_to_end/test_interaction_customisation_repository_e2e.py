from datetime import UTC, datetime

import citizen_frontend.api.repository.interaction_customisation_repository as interaction_customisation_repository


def test_get_published_customisation():
    expected_created_at = datetime(2012, 12, 12, 9, 45, 18, 807000, tzinfo=UTC)
    actual = interaction_customisation_repository.find_published_customisation("rushcliffe", "707-6-1", 0, 1)
    assert actual.created_at == expected_created_at


#
def test_find_interaction_customisation():
    expected_document_id_string = "50c8522e93867870cb0e1c1b"
    actual = interaction_customisation_repository.find_interaction_customisation("rushcliffe", "707-6-1", 0, 1)
    actual_doc_id_string = str(actual._id)
    assert actual_doc_id_string == expected_document_id_string
