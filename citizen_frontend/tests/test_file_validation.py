import io
import zipfile

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from citizen_frontend.forms.file_validation import is_accepted_mime_type


@pytest.fixture
def sample_zip_bytes() -> io.BytesIO:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("notes.txt", "hello from memory")
    buffer.seek(0)
    return buffer


def build_ooxml_bytes(entries: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for filename, content in entries.items():
            zf.writestr(filename, content)
    return buffer.getvalue()


@pytest.fixture
def valid_docx_bytes() -> bytes:
    return build_ooxml_bytes(
        {
            "[Content_Types].xml": b"<Types></Types>",
            "word/document.xml": b"<w:document></w:document>",
        }
    )


def test_is_accepted_mime_type_returns_true_simple_file_mimetype():
    expected_content = b"%PDF-1.4 fake pdf content"
    test_file = SimpleUploadedFile(name="application.pdf", content_type="application/pdf", content=expected_content)

    assert is_accepted_mime_type(test_file) is None


def test_is_accepted_mime_type_returns_true_ooxml_file(valid_docx_bytes):
    test_file = SimpleUploadedFile(name="test.docx", content_type="application/octet-stream", content=valid_docx_bytes)
    assert is_accepted_mime_type(test_file) is None


def test_is_accepted_mime_type_raises_error_zip_file(sample_zip_bytes):
    with pytest.raises(ValidationError) as e:
        is_accepted_mime_type(sample_zip_bytes)
    assert e.value.args[0] == "File is not accepted"
