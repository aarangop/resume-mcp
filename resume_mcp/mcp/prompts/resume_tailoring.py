"""
Resume Tailoring Prompts Module
"""

import logging
from pathlib import Path
from string import Template
from typing import Optional

from resume_mcp.config import OBSIDIAN_VAULT
from resume_mcp.utils.cv import generate_cv_tailoring_prompt
from resume_mcp.utils.prompt_templates import cv_generation_recipe_template

from ..base import mcp, get_app_context

logger = logging.getLogger(__name__)


@mcp.prompt(name="Tailor CV")
def tailor_resume(
    job_description: str,
    company: str,
    position: str
) -> str:
    """
    Generate a tailored resume prompt for a specific job description.

    This prompt will analyze the job requirements and create a customized version
    of your resume that emphasizes the most relevant experiences while maintaining
    100% authenticity. Never adds fictional experiences or skills.

    Args:
        job_description: The complete job description to tailor the resume for
        job_title: The job title (used for context and logging)
        company: The company name (used for context and logging)
    """
    if not job_description.strip():
        raise ValueError("Job description cannot be empty")

    # Get app context with proper typing
    app_ctx = get_app_context()

    tailored_prompt = generate_cv_tailoring_prompt(
        job_description,
        company,
        position,
        app_ctx
    )

    # Log the usage for monitoring
    logger.info(
        f"Generated resume tailoring prompt for {position} at {company}")

    return tailored_prompt


@mcp.prompt(name="Quick CV Tailor")
def quick_tailor(job_description: str, company: str, position: str) -> str:
    """
    Quick resume tailoring with minimal prompt engineering.

    A streamlined version that provides essential constraints and guidance
    for tailoring your resume to a specific job posting.

    Args:
        job_description: The job description to tailor for
    """
    if not job_description.strip():
        raise ValueError("Job description cannot be empty")

    # Get app context
    app_ctx = get_app_context()

    baseline_resume = app_ctx.resume_manager.get_baseline_content()

    return f"""You are an expert career coach helping tailor a resume for a specific job.

CRITICAL RULES:
- Use ONLY the authentic experiences provided
- NEVER add fictional companies, roles, or achievements
- NEVER invent metrics or responsibilities
- Only emphasize and reframe existing experiences

MY AUTHENTIC PROFESSIONAL BACKGROUND:
{baseline_resume}

TARGET JOB DESCRIPTION:
{position} at {company}

{job_description}

Please create a tailored resume that:
1. Emphasizes the most relevant experiences for this role
2. Uses keywords from the job description where appropriate
3. Maintains chronological accuracy
4. Highlights transferable skills
5. Stays 100% truthful to my actual background

Provide the tailored resume focusing on the experiences most relevant to this position."""


@mcp.prompt(name="Load prompt", description="Loads a specific prompt from the Obsidian vault 'prompts' directory")
def load_prompt(prompt_name: str):
    vault_path = Path(OBSIDIAN_VAULT)

    prompt_file = next(vault_path.rglob(f"prompts/{prompt_name}.md"), None)

    if not prompt_file:
        return f"No prompt named {prompt_name} found in vault"

    logger.info(f"Found at least one matching prompt file.")

    with open(prompt_file, mode='+r') as f:
        prompt = f.read()

    return prompt


@mcp.prompt(name="CV Generation Recipe", description="Kickstart a CV generation using the resume-mcp server")
def cv_generation_recipe(company: str, position: str):
    """
    Generate a recipe for CV tailoring based on a company and position.

    This function returns a tailored recipe using a predefined template for CV generation,
    filling in the provided company name and position.

    Parameters
    ----------
    company : str
        The name of the company the CV is being tailored for
    position : str
        The position title the CV is being tailored for

    Returns
    -------
    str
        A populated CV generation recipe with the company and position substituted
    """
    template = Template(cv_generation_recipe_template)
    return template.safe_substitute({
        "company": company, "position": position
    })
