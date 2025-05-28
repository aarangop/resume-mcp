import logging
from pathlib import Path
from typing import cast
from resume_mcp.config import OBSIDIAN_VAULT
from resume_mcp.mcp.base import AppContext, mcp

logger = logging.getLogger(__name__)


@mcp.resource("file://files/base-cv", name="Base CV")
def base_cv() -> str:
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)
    baseline_resume = app_ctx.resume_manager.get_baseline_content()
    return baseline_resume


@mcp.resource("file://files/latex_template", name="LaTeX Template")
def latex_template():
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)
    latex_template = app_ctx.prompt_manager.get_latex_template()
    return latex_template


@mcp.resource("obsidian://vault_index", name="Obsidian Vault File Index")
def list_vault_files() -> str:
    """
    List all markdown files in the Obsidian vault.

    Returns:
        List of available files in the vault
    """
    vault_path = Path(OBSIDIAN_VAULT)

    if not vault_path.exists():
        return f"❌ Obsidian vault not found at: {OBSIDIAN_VAULT}"

    try:
        md_files = []
        for file_path in vault_path.rglob("*.md"):
            relative_path = file_path.relative_to(vault_path)
            md_files.append(str(relative_path))

        md_files.sort()

        if not md_files:
            return f"No markdown files found in vault: {OBSIDIAN_VAULT}"

        files_by_dir = {}
        for file_path in md_files:
            dir_name = str(Path(file_path).parent) if Path(
                file_path).parent != Path('.') else "Root"
            if dir_name not in files_by_dir:
                files_by_dir[dir_name] = []
            files_by_dir[dir_name].append(Path(file_path).name)

        result = f"""# Obsidian Vault File List

**Vault Path:** {vault_path}
**Total Files:** {len(md_files)}

"""

        for dir_name, files in sorted(files_by_dir.items()):
            result += f"\n## {dir_name}\n"
            for file in sorted(files):
                result += f"- {file}\n"

        return result

    except Exception as e:
        logger.error(f"Error listing vault files: {e}")
        return f"❌ Error listing files: {str(e)}"
