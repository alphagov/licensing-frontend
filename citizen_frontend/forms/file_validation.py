import zipfile

import magic
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

OFFICE_CONTENT_TO_MIME = {
    "word/document.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "ppt/presentation.xml": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "xl/workbook.xml": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

accepted_mime_types = [
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/gif",
    "text/plain",
    "text/rtf",
    "application/rtf",
    "application/msexcel",
    "application/mspowerpoint",
    "application/msword",
    "application/vnd.ms-powerpoint",
    "application/vnd.ms-excel",
    "application/vnd.ms-word",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
]


def validate_accepted_mime_type(file_object: SimpleUploadedFile) -> None:
    file_object.seek(0)

    if zipfile.is_zipfile(file_object):
        detected_mime_type = detect_ooxml(file_object)
    else:
        sample = file_object.read(4096)
        detected_mime_type = magic.from_buffer(sample, mime=True)

    if detected_mime_type not in accepted_mime_types:
        raise ValidationError(f"File: {file_object.name} is not of an accepted file type")
    file_object.seek(0)


def detect_ooxml(file_object):
    with zipfile.ZipFile(file_object, "r") as zf:
        entries = set(zf.namelist())
        for key, value in OFFICE_CONTENT_TO_MIME.items():
            if key in entries:
                return value
        raise ValidationError(f"File: {file_object.name} is not of an accepted file type")
