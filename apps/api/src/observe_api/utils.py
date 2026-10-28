# aws_client.py
import os
from functools import lru_cache

import boto3
from botocore.client import BaseClient


@lru_cache(maxsize=1)
def get_s3_client() -> BaseClient:
    """Crea y retorna un cliente de S3.

    @lru_cache asegura que solo se cree una instancia (Singleton)
    y se reutilice en toda la aplicación.
    """
    endpoint_url = os.getenv("AWS_S3_ENDPOINT_URL", None)
    return boto3.client('s3', endpoint_url=endpoint_url, verify=False)