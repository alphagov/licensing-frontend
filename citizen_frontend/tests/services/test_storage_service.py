from io import BytesIO

import boto3
import pytest
from moto import mock_aws

from citizen_frontend.services.document_storage import S3Service


@pytest.fixture
def mock_s3_client():
    with mock_aws():
        yield boto3.client("s3", region_name="us-east-1")


@pytest.fixture
def mock_s3(mock_s3_client):
    test_bucket = mock_s3_client.create_bucket(Bucket="test-bucket")
    yield test_bucket


@pytest.fixture
def mock_service(mocker):
    service = S3Service()
    mocker.patch.object(service, "client")
    yield service


def test_s3_service_stores_file(mock_s3, mock_s3_client, mock_service):
    with open("citizen_frontend/tests/resources/Fish_Dealers_Licence.pdf", "rb") as file:
        buffer = BytesIO(file.read())
        buffer.seek(0)

    mock_service.store_file(
        path="test/file/path",
        file=buffer,
    )

    mock_service.client.upload_fileobj.assert_called()
