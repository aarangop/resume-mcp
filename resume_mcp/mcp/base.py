"""
Base MCP server configuration and shared components
"""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..config import (
    BASELINE_RESUME_PATH,
    PROMPT_TEMPLATE_PATH,
    LATEX_TEMPLATE_PATH,
    OUTPUT_DIRECTORY,
    LATEX_OUTPUT_DIR,
    SERVER_NAME
)
from ..utils.prompt_manager import PromptTemplateManager
from ..utils.resume_manager import ResumeManager

# Configure logger
logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """Application context for lifespan management"""
    prompt_manager: PromptTemplateManager
    resume_manager: ResumeManager
    output_directory: Path


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle with type-safe context"""
    logger.info("Initializing Resume Tailoring MCP Server...")

    # Initialize managers with LaTeX support
    prompt_manager = PromptTemplateManager(
        PROMPT_TEMPLATE_PATH, LATEX_TEMPLATE_PATH)
    resume_manager = ResumeManager(BASELINE_RESUME_PATH)
    output_directory = Path(OUTPUT_DIRECTORY)
    latex_output_directory = Path(LATEX_OUTPUT_DIR)

    # Ensure output directories exist
    output_directory.mkdir(parents=True, exist_ok=True)
    latex_output_directory.mkdir(parents=True, exist_ok=True)
    logger.info(
        f"Output directories ready: {output_directory}, {latex_output_directory}")

    # Validate LaTeX template
    is_valid, message = prompt_manager.validate_latex_template()
    if is_valid:
        logger.info("LaTeX template validation: ✅ Valid")
    else:
        logger.warning(f"LaTeX template validation: ⚠️ {message}")

    try:
        yield AppContext(
            prompt_manager=prompt_manager,
            resume_manager=resume_manager,
            output_directory=output_directory
        )
    finally:
        logger.info("Shutting down Resume Tailoring MCP Server...")


# Create FastMCP server with lifespan
mcp = FastMCP(SERVER_NAME, lifespan=app_lifespan)

# Add debug logging for transport detection
logger.info(f"Server initialized: {SERVER_NAME}")
logger.info("Transport will be auto-detected based on how server is invoked")
