from pathlib import Path

from observe_mcp.configure_app import get_mcp

my_mcp_server = get_mcp()


@my_mcp_server.prompt("architect-design")
def architect_design_prompt(task_description: str) -> str:
    # 1. Cargamos la plantilla desde tu archivo .md
    template_path = Path("prompts/architect-design.md")
    template = template_path.read_text(encoding="utf-8")

    # 2. Reemplazamos el marcador de posición con la descripción real
    # Usamos .replace para inyectar la tarea del usuario
    final_prompt = template.replace("{{TASK_DESCRIPTION}}", task_description)

    return final_prompt
