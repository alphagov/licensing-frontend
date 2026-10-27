import requests
from conftest import BASE_URL


# These tests require the application to be running with a seeded database
def test_get_all_licences_returns_expected_response():
    expected_subset = [
        {"code": "1324-5-1", "name": "Land drainage consents", "legislation": ["Land Drainage Act 1991"]},
        {"code": "695-5-1", "name": "Skip operator licence", "legislation": ["Highways Act 1980, Section 139"]},
    ]

    actual = requests.get(f"{BASE_URL}/api/licences")

    assert actual.status_code == 200
    for licence in expected_subset:
        assert licence in actual.json()


def test_get_licence_authorities_and_interactions_returns_expected_response():
    expected = {
        "isLocationSpecific": True,
        "geographicalAvailability": ["England", "Wales"],
        "issuingAuthorities": [
            {
                "authorityName": "City of London",
                "authoritySlug": "city-of-london",
                "authorityContact": {
                    "website": "",
                    "email": "pro@cityoflondon.gov.uk",
                    "phone": "020 7606 3030",
                    "address": "PO Box 270\nGuildhall\nEC2P 2EJ",
                },
                "authorityInteractions": {
                    "change": [
                        {
                            "url": f"{BASE_URL}/apply-for-a-licence/motor-salvage-operator-registration/"
                            f"city-of-london/change-2",
                            "usesLicensify": True,
                            "usesAuthorityUrl": False,
                            "description": "Application to surrender a registration as motor salvage operator",
                            "payment": "none",
                            "introductionText": "",
                        },
                        {
                            "url": f"{BASE_URL}/apply-for-a-licence/motor-salvage-operator-registration/"
                            f"city-of-london/change-1",
                            "usesLicensify": True,
                            "usesAuthorityUrl": False,
                            "description": "Application to change a registration as motor salvage operator",
                            "payment": "none",
                            "introductionText": "",
                        },
                    ],
                    "apply": [
                        {
                            "url": f"{BASE_URL}/apply-for-a-licence/motor-salvage-operator-registration/"
                            f"city-of-london/apply-1",
                            "usesLicensify": True,
                            "usesAuthorityUrl": False,
                            "description": "Application to register as a motor salvage operator",
                            "payment": "none",
                            "introductionText": "",
                        }
                    ],
                    "renew": [
                        {
                            "url": f"{BASE_URL}/apply-for-a-licence/motor-salvage-operator-registration/"
                            f"city-of-london/renew-1",
                            "usesLicensify": True,
                            "usesAuthorityUrl": False,
                            "description": "Application to renew a registration as motor salvage operator",
                            "payment": "none",
                            "introductionText": "",
                        }
                    ],
                },
            }
        ],
    }

    actual = requests.get(f"{BASE_URL}/api/licences/866-5-1/00AA")

    assert actual.status_code == 200
    assert expected == actual.json()
