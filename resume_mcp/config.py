"""
Configuration settings for the Resume Tailoring MCP Server
"""

import logging
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()


# Configure logger
logger = logging.getLogger(__name__)

# Server configuration
SERVER_NAME = os.getenv("SERVER_NAME", "Resume Tailoring Server")

# File paths
BASELINE_RESUME_PATH = os.getenv(
    "BASELINE_RESUME_PATH", "baseline_resume.md")
PROMPT_TEMPLATE_PATH = os.getenv(
    "PROMPT_TEMPLATE_PATH", "prompt_template.md")
LATEX_TEMPLATE_PATH = os.getenv("LATEX_TEMPLATE_PATH", "cv_template.tex")
OUTPUT_DIRECTORY = os.getenv("OUTPUT_DIRECTORY", "tailored_resumes")
OBSIDIAN_VAULT = os.getenv("OBSIDIAN_VAULT", "~/Vaults/Job Applications")

# LaTeX configuration
LATEX_COMPILER = os.getenv(
    "LATEX_COMPILER", "pdflatex")  # or xelatex, lualatex
LATEX_OUTPUT_DIR = os.getenv("LATEX_OUTPUT_DIR", "latex_output")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Template validation


def validate_paths():
    """Validate that required paths exist"""
    paths = {
        "Baseline Resume": BASELINE_RESUME_PATH,
        "Prompt Template": PROMPT_TEMPLATE_PATH,
        "LaTeX Template": LATEX_TEMPLATE_PATH,
    }

    missing = []
    for name, path in paths.items():
        if not Path(path).exists():
            missing.append(f"{name}: {path}")
    if missing:
        missing_paths = ", ".join(missing)
        logger.warning(f"The following paths weren't found: {missing_paths}")

    if not missing:
        paths_output = "\n\t".join(
            [f"{varname}:{varval}" for varname, varval in paths.items()])
        logger.info(
            f"The following paths were found: {', '.join(paths_output)}")
    return missing


# Export configuration
__all__ = [
    'SERVER_NAME',
    'BASELINE_RESUME_PATH',
    'PROMPT_TEMPLATE_PATH',
    'LATEX_TEMPLATE_PATH',
    'OUTPUT_DIRECTORY',
    'LATEX_COMPILER',
    'LATEX_OUTPUT_DIR',
    'LOG_LEVEL',
    'validate_paths'
]
