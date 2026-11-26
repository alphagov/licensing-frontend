import os
from enum import Enum, StrEnum

import clamd

from citizen_frontend.exceptions import VirusScannerUnavailableError

# allowed_mime = (
#     "application/pdf",
#     "text/plain",
#     "application/x-tika-msoffice",
#     "application/x-tika-ooxml",
#     "application/msword",
#     "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#     "application/vnd.ms-excel",
#     "application/msexcel",
#     "application/mspowerpoint",
#     "application/zip",
#     "application/rtf",
#     "text/rtf",
#     "image/jpeg",
#     "image/gif",
#     "image/png"
# )


class FileStatus(Enum):
    pass


# # TODO maybe not an service...
# # UploadDocument
# # maybe a service is better here
# class UploadValidationService:
#     def __init__(self):
#         self.virus_scanner = VirusScanner()
#
#     def validate_file(self, file):
#         self._validate_mime_type(file)
#         self.virus_scanner.scan_file(file)
#
#     def _validate_mime_type(self, file):
#         pass


class ScanResult(StrEnum):
    CLEAN = "OK"
    INFECTED = "FOUND"


class VirusScanner:
    def __init__(self):
        self.host = os.getenv("VIRUS_SCANNER_HOST")
        self.port = int(os.getenv("VIRUS_SCANNER_PORT"))
        self.is_available = self.ping()

    def scan_file(self):
        if not self.is_available:
            raise VirusScannerUnavailableError("Unable to connect to Virus Scanner")

    def ping(self):
        cd = clamd.ClamdNetworkSocket(host=self.host, port=self.port)
        response = cd.ping()
        return response == "PONG"

        # with socket.create_connection((self.host, self.port), timeout=5) as sock:
        #     sock.sendall(b"zPING\0")
        #     response = sock.recv(1024)
        #     return response == b"PONG\0"
