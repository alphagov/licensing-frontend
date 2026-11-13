from io import BytesIO


def test_s3_service_stores_file(mock_s3, mock_s3_service, mock_s3_client):
    with open("citizen_frontend/tests/resources/Fish_Dealers_Licence.pdf", "rb") as form:
        buffer = BytesIO(form.read())
        buffer.seek(0)

    # mock_application = SimpleUploadedFile(
    #     name="application.pdf",
    #     content_type="application/pdf",
    #     content=b"%PDF-1.4 fake pdf content"
    # )

    mock_s3_service.store_file(path="test/file/path", file=buffer, content_type="application/pdf")

    file = mock_s3_client.get_object(
        Bucket="test-bucket",
        Key="test/file/path",
    )

    with open("citizen_frontend/tests/resources/Fish_Dealers_Licence.pdf", "rb") as form:
        assert file["Body"].read() == form.read()


def test_store_files_handles_client_errors():
    pass
