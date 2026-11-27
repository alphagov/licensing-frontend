import io
import zipfile

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from citizen_frontend.exceptions import InvalidFileUploadException
from citizen_frontend.forms.file_validation import is_accepted_mime_type


@pytest.fixture
def sample_zip_bytes() -> io.BytesIO:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("notes.txt", "hello from memory")
    buf.seek(0)
    return buf


def test_is_accepted_mime_type_returns_true_simple_file_mimetype():
    expected_content = b"%PDF-1.4 fake pdf content"
    test_file = SimpleUploadedFile(name="application.pdf", content_type="application/pdf", content=expected_content)

    assert is_accepted_mime_type(test_file)


def test_is_accepted_mime_type_returns_true_ooxml_file():
    pass


def test_is_accepted_mime_type_raises_error_zip_file(sample_zip_bytes):
    with pytest.raises(InvalidFileUploadException) as e:
        is_accepted_mime_type(sample_zip_bytes)
    assert e.value.args[0] == "File is not accepted"


def test_is_accepted_mime_type_raises_error_when_file_is_not_allowed():
    pass
