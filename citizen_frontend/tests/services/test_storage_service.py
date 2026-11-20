from io import BytesIO

import pytest
from botocore.exceptions import ClientError

from citizen_frontend.exceptions import DocumentStorageError


def test_s3_service_stores_file(mock_s3, mock_s3_service, mock_s3_client):
    with open("citizen_frontend/tests/resources/Fish_Dealers_Licence.pdf", "rb") as form:
        buffer = BytesIO(form.read())
        buffer.seek(0)

    mock_s3_service.store_file(path="test/file/path", file=buffer, content_type="application/pdf")

    file = mock_s3_client.get_object(
        Bucket="test-bucket",
        Key="test/file/path",
    )

    with open("citizen_frontend/tests/resources/Fish_Dealers_Licence.pdf", "rb") as form:
        assert file["Body"].read() == form.read()


def test_store_files_handles_client_errors(mock_s3_service, mocker):
    mocker.patch.object(mock_s3_service, "client")
    mock_s3_service.client.upload_fileobj.side_effect = ClientError(
        error_response={"error": "upload"}, operation_name="upload"
    )

    with pytest.raises(DocumentStorageError) as e:
        mock_s3_service.store_file(path="test/file/path", file=BytesIO(), content_type="application/pdf")

    assert e.value.args[0] == "Failed to upload file to S3."
