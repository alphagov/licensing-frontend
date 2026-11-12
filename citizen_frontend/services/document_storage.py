import io
import os
from abc import ABC, abstractmethod

import boto3


class DocumentStorage(ABC):
    @abstractmethod
    def store_file(self):
        pass

    @abstractmethod
    def load(self):
        pass


class S3Service(DocumentStorage):
    def __init__(self):
        super().__init__()
        self.client = boto3.client("s3")
        self.bucket_name = os.getenv("S3_BUCKET")

    def store_file(self, path: str, file: io.BytesIO):
        self.client.upload_fileobj(file, Bucket=self.bucket_name, Key=path)

    def load(self):
        pass
