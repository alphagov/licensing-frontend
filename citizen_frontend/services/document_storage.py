import logging
import os
from abc import ABC, abstractmethod
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from citizen_frontend.exceptions import DocumentStorageError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DocumentStorage(ABC):
    @abstractmethod
    def store_file(self, *args, **kwargs):
        pass

    @abstractmethod
    def load(self):
        pass


class S3Service(DocumentStorage):
    def __init__(self):
        super().__init__()
        self.client = boto3.client("s3")
        self.bucket_name = os.getenv("S3_BUCKET")

    def store_file(self, path: str, file: BinaryIO, content_type: str | None):
        try:
            extra_args = {"ContentType": content_type} if content_type else {}

            self.client.upload_fileobj(file, Bucket=self.bucket_name, Key=path, ExtraArgs=extra_args)
        except ClientError as e:
            logger.error(e)
            raise DocumentStorageError("Failed to upload file to S3.") from e

    def load(self):
        pass
