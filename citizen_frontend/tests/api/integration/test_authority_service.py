from common.models.licences import Licence

import citizen_frontend.services.authority_service as authority_service


def test_authority_service_retrieves_correct_number_of_licences():
    licence = Licence.objects.get(licence_code="1316-4-1")

    belfast_snac_code = "95Z"

    actual = authority_service.get_authorities_for_licence_with_geographical_locator(
        locator=belfast_snac_code, licence=licence
    )

    assert actual is not None
    assert len(actual) == 4
