import logging
from typing import Optional, cast
from resume_mcp.mcp.base import AppContext, mcp

# Configure logger
logger = logging.getLogger(__name__)


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
