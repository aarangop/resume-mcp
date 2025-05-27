import logging
from typing import Optional, cast
from resume_mcp.mcp.base import AppContext, mcp

# Configure logger
logger = logging.getLogger(__name__)


@mcp.prompt()
def tailor_resume(
    job_description: str,
    job_title: Optional[str] = "Position",
    company: Optional[str] = ""
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
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    # Generate the complete prompt
    variables = {
        "baseline_resume": app_ctx.resume_manager.get_baseline_content(),
        "job_description": job_description
    }

    tailored_prompt = app_ctx.prompt_manager.substitute_variables(variables)

    # Log the usage for monitoring
    logger.info(
        f"Generated resume tailoring prompt for {job_title} at {company}")

    return tailored_prompt


@mcp.prompt()
def tailor_resume_dual_format(
    job_description: str,
    job_title: Optional[str] = "Position",
    company: Optional[str] = ""
) -> str:
    """
    Generate a tailored resume in BOTH Markdown and LaTeX formats.

    This prompt creates professionally formatted CVs in both Markdown (for easy editing)
    and LaTeX (for professional PDF compilation) that emphasize your most relevant 
    experiences while maintaining 100% authenticity.

    Args:
        job_description: The complete job description to tailor the resume for
        job_title: The job title (used for context and logging)
        company: The company name (used for context and logging)
    """
    if not job_description.strip():
        raise ValueError("Job description cannot be empty")

    # Get app context with proper typing
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    # Generate the complete prompt with LaTeX template
    variables = {
        "baseline_resume": app_ctx.resume_manager.get_baseline_content(),
        "job_description": job_description
    }

    tailored_prompt = app_ctx.prompt_manager.substitute_variables(variables)

    # Log the usage for monitoring
    logger.info(
        f"Generated dual-format resume prompt for {job_title} at {company}")

    return tailored_prompt


@mcp.prompt()
def latex_only_tailor(
    job_description: str,
    job_title: Optional[str] = "Position",
    company: Optional[str] = ""
) -> str:
    """
    Generate a tailored resume specifically in LaTeX format.

    Focus on creating a professional LaTeX CV that compiles to PDF,
    using your authentic experience tailored for the specific role.

    Args:
        job_description: The complete job description to tailor the resume for
        job_title: The job title (used for context and logging)  
        company: The company name (used for context and logging)
    """
    if not job_description.strip():
        raise ValueError("Job description cannot be empty")

    # Get app context
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    baseline_resume = app_ctx.resume_manager.get_baseline_content()
    latex_template = app_ctx.prompt_manager.get_latex_template()

    if not latex_template:
        raise ValueError("No LaTeX template available")

    return f"""You are an expert LaTeX document creator specializing in professional CVs.

CRITICAL RULES:
- Use ONLY the authentic experiences provided
- NEVER add fictional companies, roles, or achievements
- Create valid LaTeX that compiles without errors
- Follow the provided template structure exactly

MY AUTHENTIC PROFESSIONAL BACKGROUND:
{baseline_resume}

LATEX TEMPLATE TO USE:
```latex
{latex_template}
```

TARGET JOB DESCRIPTION:
{job_description}

Please create a tailored LaTeX CV that:
1. Uses the exact template structure provided
2. Emphasizes experiences most relevant to this {job_title} role
3. Incorporates keywords from the job description appropriately
4. Maintains perfect LaTeX syntax
5. Stays 100% truthful to my actual background

Provide ONLY the complete LaTeX code, ready for compilation."""


@mcp.prompt()
def quick_tailor(job_description: str) -> str:
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
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

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
{job_description}

Please create a tailored resume that:
1. Emphasizes the most relevant experiences for this role
2. Uses keywords from the job description where appropriate
3. Maintains chronological accuracy
4. Highlights transferable skills
5. Stays 100% truthful to my actual background

Provide the tailored resume focusing on the experiences most relevant to this position."""
