import logging
import os
from pathlib import Path
from typing import Optional
from resume_mcp import mcp
from resume_mcp.config import OBSIDIAN_VAULT
from resume_mcp.utils.latex import compile_latex, check_latex_server
from resume_mcp.mcp.base import mcp

logger = logging.getLogger(__name__)


@mcp.tool(
    name="compile_latex",
    description="Compiles LaTeX content and saves it into the user's vault in pdf format using a Docker-based LaTeX server."
)
def compile_latex_tool(content: str, filename: str, vault_dir: Optional[str], replace: bool = True) -> str:
    """
    Compiles LaTeX content into a PDF and saves it in the Obsidian vault.
    Uses a local Docker-based LaTeX compilation server for processing.

    Args:
        content (str): The CV content in LaTeX format
        filename (str): The name of the file to save (file extension will be forced to .pdf) 
        vault_dir (str): Directory within the Obsidian vault to save the PDF
        replace (bool): Whether to replace existing file, defaults to True
    Returns:
        str: Status message indicating success or failure
    """
    vault_path = Path(OBSIDIAN_VAULT)

    # Ensure filename has .pdf extension
    root, _ = os.path.splitext(filename)
    pdf_filename = f"{root}.pdf"

    # Create full output path
    output_dir = vault_path
    if vault_dir:
        output_dir /= vault_dir
    full_path = os.path.join(output_dir, pdf_filename)

    # Check if file exists and replace flag
    if os.path.exists(full_path) and not replace:
        return f"❌ File {pdf_filename} already exists and replace=False."

    # Check that the output directory exists
    if not os.path.exists(output_dir):
        return f"❌ Output directory '{output_dir}' does not exist. Create it first, and try again."

    # Quick server health check before attempting compilation
    server_status = check_latex_server()
    if not server_status["available"]:
        return f"❌ LaTeX Server Error: {server_status['message']}\n💡 Start the server with: docker-compose up -d"

    # Log compilation attempt
    logger.info(
        f"Calling `compile_latex` via HTTP server to destination '{full_path}'")

    # Compile LaTeX using HTTP server
    result = compile_latex(content=content, dest=full_path)

    # Process result
    if "error" in result:
        return f"❌ Error compiling PDF: {result['error']}"
    if "success" in result:
        return f"✅ Successfully compiled PDF to {result['success']['dest']}"
    return f"❓ Unexpected result from LaTeX compilation: {result}"


@mcp.tool(
    name="check_latex_server_status",
    description="Check if the LaTeX compilation server is running and healthy."
)
def check_latex_server_tool() -> str:
    """
    Check the status of the LaTeX compilation server.

    Returns:
        str: Status message about the server health and capabilities
    """
    status = check_latex_server()

    if status["available"]:
        details = status["details"]
        server_status = details.get("status", "Unknown")
        pdflatex_available = details.get("pdflatex_available", False)
        pdflatex_status = "✅ Available" if pdflatex_available else "❌ Not Available"

        return (f"✅ LaTeX Server Status: {status['message']}\n"
                f"🔧 Server Health: {server_status}\n"
                f"📦 pdflatex: {pdflatex_status}\n"
                f"🌐 Endpoint: http://localhost:7474")
    else:
        error_info = status["details"].get("error", "Unknown error")
        return (f"❌ LaTeX Server Status: {status['message']}\n"
                f"🔍 Error Details: {error_info}\n"
                f"💡 To start the server:\n"
                f"   1. Navigate to your latex-server directory\n"
                f"   2. Run: docker-compose up -d\n"
                f"   3. Verify with: curl http://localhost:7474/health")


@mcp.tool(
    name="start_latex_server_help",
    description="Get instructions on how to start the LaTeX server."
)
def start_latex_server_help() -> str:
    """
    Provide detailed instructions for starting the LaTeX compilation server.

    Returns:
        str: Step-by-step instructions for starting the server
    """
    return """🚀 LaTeX Server Setup Instructions

**Prerequisites:**
- Docker or Podman installed
- LaTeX server repository/files available

**Starting the Server:**

1. **Navigate to server directory:**
   ```bash
   cd /path/to/your/latex-server
   ```

2. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   # OR with Podman:
   podman-compose up -d
   ```

3. **Verify server is running:**
   ```bash
   curl http://localhost:7474/health
   ```

4. **View server logs (if needed):**
   ```bash
   docker-compose logs -f latex-server
   ```

**Troubleshooting:**
- Port 7474 in use? Check: `lsof -i :7474`
- Server won't start? Check logs: `docker-compose logs latex-server`
- Need to rebuild? Run: `docker-compose up -d --build`

**Testing the Server:**
Once running, you can test with a simple LaTeX document using the MCP tools or via curl.
"""
