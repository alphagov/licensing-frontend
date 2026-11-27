from django.core.files.uploadedfile import SimpleUploadedFile

from citizen_frontend.forms.file_validation import is_accepted_mime_type


def test_is_accepted_mime_type_returns_true_simple_file_mimetype():
    expected_content = b"%PDF-1.4 fake pdf content"
    test_file = SimpleUploadedFile(name="application.pdf", content_type="application/pdf", content=expected_content)

    assert is_accepted_mime_type(test_file)
