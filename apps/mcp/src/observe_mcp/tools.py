"""This module provides tools for working with Observer MCP Assistant."""

import os
import re

import httpx

from observe_mcp.configure_app import get_mcp

my_mcp_server = get_mcp()

API_BASE_URL = os.getenv("API_BASE_URL", "http://observer_api:8000/")

# Farewell detection — used to short-circuit with a goodbye message.
_FAREWELL_RE = re.compile(
    r"\b(bye|goodbye|ciao|later|see\s+you|hasta\s+luego|au\s+revoir|arrivederci|auf\s+wiedersehen)\b",
    re.IGNORECASE,
)

# Common single-word greetings/filler and ID label prefixes to strip before extracting the name.
# DNI:? / NIF:? handles inputs like "DNI 12345678A".
_NOISE_RE = re.compile(
    r"\b(hello|hi|hey|howdy|hola|ciao|bonjour|salut|bonsoir|buongiorno|buonasera|"
    r"hallo|ol\u00e1|saludos|buenas|good\s*(morning|afternoon|evening|day)|"
    r"guten\s*(morgen|tag|abend)|bom\s*(dia|tarde|noite)|DNI:?|NIF:?)\b",
    re.IGNORECASE,
)

# DNI/NIF pattern: 7-9 digits followed by a letter (e.g. 12345678A, 666666666J).
_DNI_RE = re.compile(r"\b[0-9]{7,9}[A-Za-z]\b")


@my_mcp_server.tool(
    name="hello_world",
    description=(
        "Observer MCP Assistant entry point. Greets the user, introduces itself, "
        "and collects the name and national ID (DNI/NIF) needed to personalize "
        "subsequent financial service calls."
    ),
)
async def hello_world(user: str) -> str:
    """Greets the user and collects their name and national ID (DNI/NIF).

    This is the entry-point tool for the Observer MCP Assistant.  It introduces
    the assistant and, if the caller has not yet provided both a full name and
    a national ID, it asks for them up-front so that all subsequent tool calls
    (account balances, transactions, card movements, etc.) can be personalized
    without prompting for identity again.

    Logic:
      - Farewell keyword detected  -> polite goodbye.
      - DNI present, name missing  -> ask for the name.
      - Name present, DNI missing  -> ask for the DNI.
      - Both present               -> confirm and invite next question.
      - Neither present            -> introduce assistant and ask for both.

    Args:
        user (str): Any input from the user -- a greeting, a name, an ID,
                    or all three together (e.g. "hola Juan Garcia 12345678A").

    Returns:
        str: A short, focused reply from the Observer MCP Assistant.
    """
    # Farewell short-circuit.
    if _FAREWELL_RE.search(user):
        return "Goodbye! The Observer MCP Assistant is always here when you need it."

    has_dni = bool(_DNI_RE.search(user))
    # Strip greeting noise and DNI token; what remains is the candidate name.
    name_part = _NOISE_RE.sub("", user)
    name_part = _DNI_RE.sub("", name_part).strip()
    has_name = len(name_part) > 1

    if not has_name and not has_dni:
        return (
            "Hi! I'm the **Observer MCP Assistant**, your digital observer helper.\n"
            "To get started, please tell me your **full name** and **national ID (DNI/NIF)**."
        )
    if not has_dni:
        return (
            f"Hi, {name_part}! I'm the **Observer MCP Assistant**.\n"
            "Could you also provide your **national ID (DNI/NIF)** so I can access your account?"
        )
    if not has_name:
        return (
            "I'm the **Observer MCP Assistant**. I have your ID -- "
            "could you also share your **full name** so I can address you correctly?"
        )

    return f"Welcome, {name_part}! I'm the **Observer MCP Assistant**. Identity confirmed. How can I help you today?"


@my_mcp_server.tool(
    name="execute_route",
    description="Just call to another RestAPI and get its version.",
)
async def execute_route(name: str) -> str:
    """Just call to another RestAPI and get its version.

    Returns:
        str: A short, focused reply from the Observer MCP Assistant.
    """
    # Build target URL from environment or use localhost default.
    base_url = os.getenv("OBSERVER_ROUTE_BASE", "http://observe_api:8000")
    route_url = f"{base_url.rstrip('/')}/route"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(route_url, params={"name": name})
            resp.raise_for_status()

            # Prefer JSON 'version' field if present, otherwise use text.
            try:
                data = resp.json()
                if isinstance(data, dict) and "version" in data:
                    return f"Remote route response: {data!s}"
            except Exception:
                pass

            text = resp.text.strip()
            if text:
                return f"Remote route response: {text}"

            return "Remote route returned no content."
    except httpx.HTTPStatusError as e:
        return f"Remote route returned HTTP {e.response.status_code}: {e.response.text}"
    except Exception as e:
        return f"Error contacting remote route: {e}"


@my_mcp_server.tool(
    name="get_secret",
    description="Recupera el contenido de un archivo específico almacenado en el bucket de S3.\n"
                "Esta herramienta accede a la clave proporcionada y devuelve el texto decodificado.\n"
                "Útil cuando necesitas consultar el valor de un secreto o configuración guardada."
)
async def get_secret(file_key: str) -> str:
    """
    Retrieve a specific secret file content from S3.

    Args:
        file_key (str): The unique identifier/key of the file in the S3 bucket.

    Returns:
        str: The content of the secret file or an error message if the operation fails.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/get-secret/{file_key}")
        if response.status_code == 200:
            return str(response.json())
        return f"Error {response.status_code}: {response.text}"

@my_mcp_server.tool(
    name="list_secrets",
    description="Obtiene un listado completo de todos los nombres de archivo disponibles en el bucket.\n"
                "Analiza el bucket configurado y extrae la lista de las claves presentes en el sistema.\n"
                "Ideal para explorar qué secretos están almacenados antes de realizar una consulta."
)
async def list_secrets() -> list:
    """
    List all available secret keys in the S3 bucket.

    Returns:
        list: A list of string keys present in the bucket, or an empty list if none found.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/list-secrets")
        if response.status_code == 200:
            return response.json().get("files", [])
        return [f"Error: {response.text}"]

@my_mcp_server.tool(
    name="save_secret",
    description="Crea o sobrescribe un archivo en S3 utilizando una clave y contenido de texto plano.\n"
                "Esta herramienta toma el par clave-valor y lo almacena directamente en el bucket.\n"
                "Se utiliza para persistir configuraciones o credenciales mediante una entrada de texto."
)
async def save_secret(key: str, content: str) -> str:
    """
    Save or overwrite a secret in S3 with provided content.

    Args:
        key (str): The destination path or filename in the bucket.
        content (str): The raw text content to store.

    Returns:
        str: A confirmation message or an error description.
    """
    async with httpx.AsyncClient() as client:
        payload = {"key": key, "content": content}
        response = await client.post(f"{API_BASE_URL}/save-secret", json=payload)
        if response.status_code == 200:
            return response.json().get("message", "Guardado con éxito")
        return f"Error: {response.text}"

@my_mcp_server.tool(
    name="upload_secret",
    description="Carga un archivo binario o de texto desde el sistema local hacia el bucket de S3.\n"
                "Permite asignar una clave específica al archivo durante el proceso de transferencia.\n"
                "Útil para subir configuraciones desde archivos existentes en lugar de escribir texto."
)
async def upload_secret(key: str, file_path: str) -> str:
    """
    Upload a local file to the S3 bucket.

    Args:
        key (str): The target key name for the stored file.
        file_path (str): The absolute or relative path to the file on the local disk.

    Returns:
        str: A confirmation message upon successful upload or an error string.
    """
    async with httpx.AsyncClient() as client:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            params = {'key': key}
            response = await client.post(f"{API_BASE_URL}/upload-secret", params=params, files=files)
            if response.status_code == 200:
                return response.json().get("message", "Subido con éxito")
            return f"Error: {response.text}"