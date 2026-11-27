import magic

accepted_mime_to_exts = {
    "application/pdf": {".pdf"},
    "image/png": {".png"},
    "image/jpeg": {".jpg", ".jpeg"},
    "text/plain": {".txt"},
    "text/rtf": {".rtf"},
}

accepted_mime_types = ["application/pdf", "image/png", "image/jpeg", "text/plain", "text/rtf"]


def is_accepted_mime_type(file) -> bool:
    file.seek(0)
    sample = file.read(4096)

    detected_mime_type = magic.from_buffer(sample, mime=True)
    return detected_mime_type in accepted_mime_to_exts
