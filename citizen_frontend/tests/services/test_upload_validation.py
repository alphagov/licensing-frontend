import tempfile

import pytest

from citizen_frontend.exceptions import VirusScannerUnavailableError
from citizen_frontend.services.upload_validation import ScanResult, VirusScanner


def test_virus_scanner_connection_ping():
    scanner = VirusScanner()
    assert scanner.ping()


def test_scan_files_throws_error_scanner_unavailable():
    scanner = VirusScanner()
    scanner.is_available = False

    with pytest.raises(VirusScannerUnavailableError):
        with open("citizen_frontend/tests/resources/Fish_Dealers_Licence.pdf", "rb") as f:
            scanner.scan_file(f)


def test_scan_files_returns_ok_result_when_scanning_clean_file():
    scanner = VirusScanner()
    with open("citizen_frontend/tests/resources/Fish_Dealers_Licence.pdf", "rb") as f:
        result = scanner.scan_file(f)
    assert result == ScanResult.CLEAN


def test_scan_files_returns_infected_when_scanning_infected_file():
    scanner = VirusScanner()
    with tempfile.TemporaryFile(mode="w+b") as file:
        file.write(b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR" + b"-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*")
        file.seek(0)
        result = scanner.scan_file(file)
    assert result == ScanResult.INFECTED
