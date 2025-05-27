"""
Resume Tailoring MCP Server
Provides AI-powered resume tailoring through reusable MCP prompt templates
"""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, cast

from mcp.server.fastmcp import FastMCP, Context

from resume_mcp.config import (
    BASELINE_RESUME_PATH,
    PROMPT_TEMPLATE_PATH,
    OUTPUT_DIRECTORY,
    SERVER_NAME,
)
from .utils.prompt_manager import PromptTemplateManager
from .utils.resume_manager import ResumeManager

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

    # Initialize managers
    prompt_manager = PromptTemplateManager(PROMPT_TEMPLATE_PATH)
    resume_manager = ResumeManager(BASELINE_RESUME_PATH)
    output_directory = Path(OUTPUT_DIRECTORY)

    # Ensure output directory exists
    output_directory.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory ready: {output_directory}")

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

# =============================================================================
# PROMPT DEFINITIONS
# =============================================================================


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


@mcp.prompt()
def analyze_job_fit(job_description: str) -> str:
    """
    Analyze how well your background fits a specific job posting.

    This prompt helps you understand your strengths and potential gaps
    for a particular role based on your authentic experience.

    Args:
        job_description: The job description to analyze fit against
    """
    if not job_description.strip():
        raise ValueError("Job description cannot be empty")

    # Get app context
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    baseline_resume = app_ctx.resume_manager.get_baseline_content()

    return f"""You are a career counselor analyzing job fit based on authentic professional experience.

MY PROFESSIONAL BACKGROUND:
{baseline_resume}

TARGET JOB POSTING:
{job_description}

Please provide a detailed analysis covering:

1. **STRENGTHS** - Which aspects of my background align well with this role?
2. **TRANSFERABLE SKILLS** - What skills from my experience apply to their needs?
3. **POTENTIAL GAPS** - What requirements might I need to address or learn?
4. **UNIQUE VALUE** - How does my background offer something distinctive?
5. **APPLICATION STRATEGY** - How should I position myself for this role?

Be honest about both strengths and areas for development. Focus on authentic experiences only."""


@mcp.prompt()
def cover_letter_prompt(
    job_description: str,
    company_research: Optional[str] = ""
) -> str:
    """
    Generate a personalized cover letter based on your authentic experience.

    Creates a compelling cover letter that connects your real background
    to the specific role and company.

    Args:
        job_description: The job description for the role
        company_research: Optional additional information about the company
    """
    if not job_description.strip():
        raise ValueError("Job description cannot be empty")

    # Get app context
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    baseline_resume = app_ctx.resume_manager.get_baseline_content()

    company_context = f"\n\nADDITIONAL COMPANY CONTEXT:\n{company_research}" if company_research else ""

    return f"""You are a professional writer helping create a compelling cover letter.

IMPORTANT CONSTRAINTS:
- Use ONLY authentic experiences from my background
- NEVER fabricate achievements or experiences
- Connect real experiences to job requirements
- Be genuine and professional

MY PROFESSIONAL BACKGROUND:
{baseline_resume}

JOB DESCRIPTION:
{job_description}{company_context}

Please write a cover letter that:
1. Opens with genuine enthusiasm for the role
2. Connects 2-3 specific experiences to key job requirements
3. Shows understanding of the company/role
4. Demonstrates authentic interest and cultural fit
5. Closes with confidence and next steps

Keep it concise (3-4 paragraphs) and authentic. Use specific examples from my real experience."""


@mcp.prompt()
def interview_prep(
    job_description: str,
    interview_type: Optional[str] = "general"
) -> str:
    """
    Generate interview preparation based on your background and the job requirements.

    Creates tailored interview questions and guidance based on your authentic
    experience and the specific role requirements.

    Args:
        job_description: The job description for the role
        interview_type: Type of interview (general, technical, behavioral, etc.)
    """
    if not job_description.strip():
        raise ValueError("Job description cannot be empty")

    # Get app context
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

    baseline_resume = app_ctx.resume_manager.get_baseline_content()

    return f"""You are an experienced interview coach preparing a candidate for a {interview_type} interview.

MY PROFESSIONAL BACKGROUND:
{baseline_resume}

TARGET JOB DESCRIPTION:
{job_description}

Please provide comprehensive interview preparation including:

1. **LIKELY QUESTIONS** - Based on the job requirements, what questions should I expect?
2. **ANSWER FRAMEWORKS** - How should I structure my responses using my real experience?
3. **KEY STORIES** - Which of my experiences should I highlight for different question types?
4. **TECHNICAL PREPARATION** - What technical topics should I review based on the role?
5. **QUESTIONS TO ASK** - What intelligent questions should I ask the interviewer?
6. **POTENTIAL CONCERNS** - What gaps might they probe, and how should I address them?

Focus on connecting my authentic experiences to their needs. Provide specific examples from my background."""

# =============================================================================
# MANAGEMENT TOOLS
# =============================================================================


@mcp.tool()
def reload_templates() -> str:
    """
    Reload prompt template and baseline resume from files.
    Useful when you've updated the template or resume files.

    Returns:
        Status message indicating success or failure
    """
    try:
        # Get app context with proper typing
        ctx = mcp.get_context()
        app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

        app_ctx.prompt_manager.reload_template()
        app_ctx.resume_manager.reload_baseline()

        logger.info("Templates reloaded successfully")
        return "✅ Successfully reloaded prompt template and baseline resume from files"
    except Exception as e:
        error_msg = f"❌ Error reloading templates: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
def get_server_status() -> str:
    """
    Get the current status and configuration of the resume tailoring server.

    Returns:
        Server status information
    """
    try:
        # Get app context with proper typing
        ctx = mcp.get_context()
        app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

        # Check file existence
        template_exists = app_ctx.prompt_manager.template_path.exists()
        resume_exists = app_ctx.resume_manager.resume_path.exists()

        # Get some basic stats
        baseline_length = len(app_ctx.resume_manager.get_baseline_content())

        return f"""# Resume Tailoring Server Status

## Configuration
- **Server Name:** {SERVER_NAME}
- **Baseline Resume Path:** {app_ctx.resume_manager.resume_path}
- **Prompt Template Path:** {app_ctx.prompt_manager.template_path}
- **Output Directory:** {app_ctx.output_directory}

## File Status
- **Baseline Resume:** {'✅ Found' if resume_exists else '❌ Not Found'}
- **Prompt Template:** {'✅ Found' if template_exists else '❌ Not Found'}
- **Output Directory:** {'✅ Ready' if app_ctx.output_directory.exists() else '❌ Not Found'}

## Content Stats
- **Baseline Resume Length:** {baseline_length} characters

## Available Prompts
- **tailor_resume** - Full-featured resume tailoring prompt
- **quick_tailor** - Streamlined resume tailoring
- **analyze_job_fit** - Job fit analysis
- **cover_letter_prompt** - Cover letter generation
- **interview_prep** - Interview preparation guidance

## Available Tools
- **reload_templates** - Refresh files from disk
- **get_server_status** - This status information

## Usage
Use the prompts directly in your MCP client (Claude Desktop, etc.) by providing job descriptions.
The server maintains your authentic professional background and applies sophisticated prompt engineering.
"""
    except Exception as e:
        error_msg = f"❌ Error getting server status: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool()
def validate_configuration() -> str:
    """
    Validate that all required files and configurations are properly set up.

    Returns:
        Validation report with recommendations
    """
    try:
        # Get app context
        ctx = mcp.get_context()
        app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

        issues = []
        recommendations = []

        # Check baseline resume
        if not app_ctx.resume_manager.resume_path.exists():
            issues.append("❌ Baseline resume file not found")
            recommendations.append(
                "Create your baseline resume at the configured path")
        else:
            content = app_ctx.resume_manager.get_baseline_content()
            if len(content) < 500:
                issues.append("⚠️ Baseline resume seems very short")
                recommendations.append(
                    "Ensure your baseline resume is comprehensive")

        # Check template
        if not app_ctx.prompt_manager.template_path.exists():
            issues.append("❌ Prompt template file not found")
            recommendations.append("Template will use built-in default")

        # Check output directory
        if not app_ctx.output_directory.exists():
            issues.append("⚠️ Output directory doesn't exist")
            recommendations.append("Directory will be created automatically")

        # Generate report
        status = "✅ All Good" if not issues else f"⚠️ {len(issues)} Issues Found"

        report = f"""# Configuration Validation Report

## Status: {status}

## Issues Found:
"""
        if issues:
            for issue in issues:
                report += f"- {issue}\n"
        else:
            report += "- No issues detected\n"

        report += "\n## Recommendations:\n"
        if recommendations:
            for rec in recommendations:
                report += f"- {rec}\n"
        else:
            report += "- Configuration looks good!\n"

        return report

    except Exception as e:
        return f"❌ Error validating configuration: {str(e)}"
