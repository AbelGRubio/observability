import os

from observe_mcp.configure_app import get_mcp

my_mcp_server = get_mcp()


def load_md_file(filename: str) -> str:
    # Asegúrate de que la ruta sea relativa a la raíz de tu proyecto
    # o donde se ejecute el servidor MCP
    filepath = os.path.join("resources", filename)

    if not os.path.exists(filepath):
        return f"Error: No se encontró el archivo {filename}"

    with open(filepath, encoding="utf-8") as f:
        return f.read()


@my_mcp_server.resource("file://docs/{filename}", mime_type="text/markdown")
def read_documentation(filename: str) -> str:
    """Lee archivos markdown desde la carpeta resources.

    Ejemplo de URI: file://docs/software_engineering_principles.md
    """
    return load_md_file(filename)


@my_mcp_server.resource("file://docs/conventions", mime_type="text/markdown")
def read_conventions() -> str:
    """Lee archivos markdown desde la carpeta resources.

    Ejemplo de URI: file://docs/conventions.md
    """
    return load_md_file("conventions.md")


@my_mcp_server.resource("file://docs/agents", mime_type="text/markdown")
def read_agents() -> str:
    """Lee archivos markdown desde la carpeta resources.

    Ejemplo de URI: file://docs/agents.md
    """
    return load_md_file("agents.md")
