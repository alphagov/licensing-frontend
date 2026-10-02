from common.models.licences import Licence
from conftest import TEST_LICENCE

import citizen_frontend.api.repository.licence_repository as licence_repository


def test_get_licence_by_licence_code_returns_none_when_no_licence_matches(mock_get_licence):
    mock_get_licence.side_effect = Licence.DoesNotExist

    actual = licence_repository.get_licence_by_licence_code(TEST_LICENCE.licence_code)

    mock_get_licence.assert_called_with(licence_code=TEST_LICENCE.licence_code)
    assert actual is None
