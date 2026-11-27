import magic

from citizen_frontend.exceptions import InvalidFileUploadException

accepted_mime_to_exts = {
    "application/pdf": {".pdf"},
    "image/png": {".png"},
    "image/jpeg": {".jpg", ".jpeg"},
    "text/plain": {".txt"},
    "text/rtf": {".rtf"},
}


OFFICE_ZIP_MARKERS = {
    ".docx": "word/document.xml",
    ".xlsx": "xl/workbook.xml",
    ".pptx": "ppt/presentation.xml",
}
accepted_mime_types = ["application/pdf", "image/png", "image/jpeg", "text/plain", "text/rtf"]


def is_accepted_mime_type(file_bytes) -> bool:
    file_bytes.seek(0)
    sample = file_bytes.read(4096)

    detected_mime_type = magic.from_buffer(sample, mime=True)
    if detected_mime_type not in accepted_mime_to_exts:
        raise InvalidFileUploadException("File is not accepted")
