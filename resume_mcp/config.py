#!/usr/bin/env python3
"""
Configuration module for resume tailoring
"""

import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logger
logger = logging.getLogger(__name__)

# Default configuration
BASELINE_RESUME_PATH = os.getenv(
    "BASELINE_RESUME_PATH", "./baseline_resume.md")
PROMPT_TEMPLATE_PATH = os.getenv(
    "PROMPT_TEMPLATE_PATH", "./prompt_template.md")
OUTPUT_DIRECTORY = os.getenv("OUTPUT_DIRECTORY", "./tailored_resumes")
SERVER_NAME = "CV Assistant"

# Ensure paths are expanded
BASELINE_RESUME_PATH = os.path.expanduser(BASELINE_RESUME_PATH)
PROMPT_TEMPLATE_PATH = os.path.expanduser(PROMPT_TEMPLATE_PATH)
OUTPUT_DIRECTORY = os.path.expanduser(OUTPUT_DIRECTORY)

varnames = "BASELINE_RESUME_PATH", "PROMPT_TEMPLATE_PATH", "OUTPUT_DIRECTORY"
varvals = BASELINE_RESUME_PATH, PROMPT_TEMPLATE_PATH, OUTPUT_DIRECTORY
varsoutput = "\n\t - ".join([f"{varname}: {varval}" for varname,
                             varval in zip(varnames, varvals)])

logger.info(f"Set up config variables: {varsoutput}")
