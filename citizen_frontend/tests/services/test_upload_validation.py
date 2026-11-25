# from citizen_frontend.services.upload_validation import UploadValidationService
import pytest

from citizen_frontend.exceptions import VirusScannerUnavailableError
from citizen_frontend.services.upload_validation import VirusScanner

#
# def test_service_validates_file_mime_type():
#     service = UploadValidationService()
#     service._validate_mime_type()


# File mimetype validation could happen on the form class inside .clean() METHOD
# Start on virus scanning,


def test_clam_av_ping():
    scanner = VirusScanner()
    assert scanner.ping()


def test_scan_files_throws_error_scanner_unavailable():
    scanner = VirusScanner()
    scanner.is_available = False

    with pytest.raises(VirusScannerUnavailableError):
        scanner.scan_file()
