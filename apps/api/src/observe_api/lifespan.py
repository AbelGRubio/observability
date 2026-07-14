from contextlib import asynccontextmanager

from botocore.exceptions import ClientError
from fastapi import FastAPI
from observe_core.logger import get_logger

from observe_api.utils import get_s3_client

logger = get_logger(__name__)

BUCKET_NAME = "my-bucket"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- LOGIC STARTUP ---
    logger.info("Iniciando verificación de infraestructura en MiniStack...")
    s3_client = get_s3_client()
    tags_deseadas = {
        'Environment': 'Development',
        'Project': 'MiniStack-Test'}

    try:
        # 1. ¿Existe el bucket?
        s3_client.head_bucket(Bucket=BUCKET_NAME)
        logger.info(f"El bucket '{BUCKET_NAME}' existe.")

    except ClientError:
        logger.info(f"El bucket '{BUCKET_NAME}' no existe. Creando...")
        s3_client.create_bucket(Bucket=BUCKET_NAME)

    for key, content in tags_deseadas.items():
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=content.encode('utf-8')
        )
        logger.info(f"Update variable {key}")

    yield
    # --- LOGIC SHUTDOWN ---
    logger.info("Cerrando aplicación...")