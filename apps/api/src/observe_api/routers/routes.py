"""Versioned API route definitions."""


from botocore.client import BaseClient
from botocore.exceptions import ClientError
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from observe_core.logger import get_logger
from opentelemetry import trace
from pydantic import BaseModel

from observe_api.config import __version__
from observe_api.utils import get_s3_client

v1_router = APIRouter()
logger = get_logger(__name__)

BUCKET_NAME = "my-bucket"

@v1_router.get("/route")
def route(name: str) -> JSONResponse:
    """Return a sample versioned response for the given name."""
    status_code = 200
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("my-operation") as span:
        span.add_event("Start doing operation")

        # Placeholder business logic.
        user_id = 123

        span.add_event(
            "User processed", {"user.id": f"{name}:{user_id}", "result": "ok"}
        )
    logger.info("Doing things here")
    return JSONResponse(
        content={f"{name}, the version is": __version__}, status_code=status_code
    )


@v1_router.get("/get-secret/{file_key}")
async def get_secret_from_s3(file_key: str):
    try:
        s3_client = get_s3_client()
        # Descargamos el objeto desde S3
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)

        # Leemos el contenido
        secret_content = response['Body'].read().decode('utf-8')

        return {"filename": file_key, "secret": secret_content}

    except ClientError as e:
        # Capturamos errores específicos de AWS (ej. archivo no encontrado)
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchKey':
            raise HTTPException(status_code=404, detail="El archivo no existe en S3")
        raise HTTPException(status_code=500, detail=f"Error de AWS: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@v1_router.get("/list-secrets")
async def list_secrets(s3: BaseClient = Depends(get_s3_client)):
    try:
        # 'list_objects_v2' es la forma recomendada para listar objetos
        response = s3.list_objects_v2(Bucket=BUCKET_NAME)

        # Verificamos si el bucket tiene contenido
        if 'Contents' not in response:
            return {"files": []}

        # Extraemos solo los nombres (Key) de los archivos
        files = [obj['Key'] for obj in response['Contents']]
        return {"files": files}

    except Exception as e:
        return {"error": str(e)}


class SecretModel(BaseModel):
    key: str      # Ejemplo: "config/db_password.txt"
    content: str  # Ejemplo: "mi_contraseña_secreta_123"


@v1_router.post("/save-secret")
async def save_secret(secret: SecretModel, s3: BaseClient = Depends(get_s3_client)):
    try:
        # put_object sube el contenido al bucket
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=secret.key,
            Body=secret.content.encode('utf-8') # El contenido debe ser bytes
        )
        return {"message": f"Secreto '{secret.key}' guardado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@v1_router.post("/upload-secret")
async def upload_secret(key: str, file: UploadFile = File(...), s3: BaseClient = Depends(get_s3_client)):
    # Lee el contenido del archivo subido
    content = await file.read()
    s3.put_object(Bucket=BUCKET_NAME, Key=key, Body=content)
    return {"message": "Archivo subido correctamente"}
