import logging
import os
from pathlib import Path
import requests
from typing import Dict

from resume_mcp.config import LATEX_SERVER_URL

logger = logging.getLogger(__name__)

# Configuration
LATEX_SERVER_TIMEOUT = 60  # seconds


def check_latex_server() -> Dict:
    """
    Check if the LaTeX compilation server is running and healthy.

    Returns:
        Dict: {"available": bool, "message": str, "details": dict}
    """
    try:
        response = requests.get(f"{LATEX_SERVER_URL}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            return {
                "available": True,
                "message": "LaTeX server is running and healthy",
                "details": health_data
            }
        else:
            return {
                "available": False,
                "message": f"LaTeX server responded with status {response.status_code}",
                "details": {}
            }
    except requests.exceptions.RequestException as e:
        return {
            "available": False,
            "message": "LaTeX server is not running",
            "details": {"error": str(e)}
        }


def compile_latex_http(content: str, dest: str) -> Dict:
    """
    Compiles LaTeX content to PDF using the HTTP LaTeX server.

    Args:
        content (str): LaTeX source content to compile
        dest (str): Destination path for the output PDF file
    Returns:
        Dict: {"success": {"dest": path}} or {"error": error_message}
    """
    dest_path = Path(dest)
    filename = dest_path.stem

    try:
        # Check if server is available first
        server_status = check_latex_server()
        if not server_status["available"]:
            return {"error": f"{server_status['message']}. Please start the LaTeX server with: docker-compose up -d"}

        # Check if pdflatex is available on the server
        health_data = server_status["details"]
        if not health_data.get("pdflatex_available", False):
            return {"error": "pdflatex is not available on the LaTeX server"}

        # Prepare request payload
        payload = {
            "content": content,
            "filename": filename
        }

        # Make compilation request
        logger.info(
            f"Sending LaTeX compilation request to {LATEX_SERVER_URL}/compile")
        response = requests.post(
            f"{LATEX_SERVER_URL}/compile",
            json=payload,
            timeout=LATEX_SERVER_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            # Save the PDF content to destination
            with open(dest, "wb") as f:
                f.write(response.content)

            logger.info(f"PDF compiled and saved successfully to {dest}")
            return {"success": {"dest": dest}}
        else:
            # Handle error response
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except:
                error_detail = response.text[:500] if response.text else "Unknown error"

            return {"error": f"LaTeX compilation failed: {error_detail}"}

    except requests.exceptions.Timeout:
        return {"error": "LaTeX compilation timed out (server took too long)"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error communicating with LaTeX server: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error during LaTeX compilation: {str(e)}"}


def compile_latex(content: str, dest: str) -> Dict:
    """
    Compiles LaTeX content to a PDF file using the HTTP LaTeX server.

    This function replaces the previous subprocess-based compilation with
    HTTP requests to a dockerized LaTeX compilation server.

    Args:
        content (str): LaTeX source content to compile
        dest (str): Destination path for the output PDF file
    Returns:
        Dict: A dictionary with one of the following structures:
            - {"success": {"dest": path_to_pdf}} if compilation succeeds
            - {"error": error_message} if compilation fails

    Note:
        This function requires the LaTeX compilation server to be running on localhost:7474.
        Start the server with: docker-compose up -d
    """
    logger.info(f"Compiling LaTeX content via HTTP server to: {dest}")

    # Use HTTP-based compilation
    result = compile_latex_http(content, dest)

    # Log the result
    if "success" in result:
        logger.info(
            f"LaTeX compilation successful: {result['success']['dest']}")
    else:
        logger.error(f"LaTeX compilation failed: {result['error']}")

    return result

# Legacy function for backwards compatibility (now deprecated)


def check_pdflatex() -> bool:
    """
    Check if the LaTeX server is available instead of local pdflatex.

    This function is kept for backwards compatibility but now checks
    the HTTP LaTeX server instead of local pdflatex installation.

    Returns:
        bool: True if LaTeX server is available, False otherwise.
    """
    logger.warning(
        "check_pdflatex() is deprecated. Use check_latex_server() instead.")
    server_status = check_latex_server()
    return server_status["available"] and server_status["details"].get("pdflatex_available", False)
