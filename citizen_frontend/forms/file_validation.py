import zipfile

import magic

from citizen_frontend.exceptions import InvalidFileUploadException

OFFICE_CONTENT_TO_MIME = {
    "word/document.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "ppt/presentation.xml": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "xl/workbook.xml": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
}

accepted_mime_types = [
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/giftext/plain",
    "text/rtf",
    "application/msexcel",
    "application/mspowerpoint",
    "application/msword",
    "application/vnd.ms-powerpoint",
    "application/vnd.ms-excel",
    "application/vnd.ms-word",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
]


def is_accepted_mime_type(file_bytes) -> bool:
    file_bytes.seek(0)

    if zipfile.is_zipfile(file_bytes):
        detected_mime_type = detect_ooxml(file_bytes)
    else:
        sample = file_bytes.read(4096)
        detected_mime_type = magic.from_buffer(sample, mime=True)

    if detected_mime_type not in accepted_mime_types:
        raise InvalidFileUploadException("File is not accepted")
    file_bytes.seek(0)
    return True


def detect_ooxml(file_bytes):
    with zipfile.ZipFile(file_bytes, "r") as zf:
        entries = set(zf.namelist())
        for key, value in OFFICE_CONTENT_TO_MIME.items():
            if key in entries:
                return value
            else:
                raise InvalidFileUploadException("File is not accepted")
        return None
