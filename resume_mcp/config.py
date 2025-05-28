"""
Configuration settings for the Resume Tailoring MCP Server
"""

import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Server configuration
SERVER_NAME = os.getenv("SERVER_NAME", "Resume Tailoring Server")

# File paths - Updated for new structure with templates/ directory
BASELINE_RESUME_PATH = os.getenv(
    "BASELINE_RESUME_PATH", "./templates/baseline_resume.md")
PROMPT_TEMPLATE_PATH = os.getenv(
    "PROMPT_TEMPLATE_PATH", "./templates/prompt_template.md")
LATEX_TEMPLATE_PATH = os.getenv(
    "LATEX_TEMPLATE_PATH", "./templates/latex_template.tex")
OUTPUT_DIRECTORY = os.getenv(
    "OUTPUT_DIRECTORY", "./templates/tailored_resumes")

# Obsidian vault configuration
OBSIDIAN_VAULT = os.getenv("OBSIDIAN_VAULT", "./obsidian_vault")

# LaTeX configuration
LATEX_COMPILER = os.getenv(
    "LATEX_COMPILER", "pdflatex")  # or xelatex, lualatex
LATEX_OUTPUT_DIR = os.getenv("LATEX_OUTPUT_DIR", "./templates/latex_output")

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
    'OBSIDIAN_VAULT',
    'LOG_LEVEL',
    'validate_paths'
]
