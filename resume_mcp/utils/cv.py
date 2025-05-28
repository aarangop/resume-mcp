import logging
import os
import re
from typing import Any, Dict
from resume_mcp.config import OBSIDIAN_VAULT, OUTPUT_DIRECTORY
from resume_mcp.mcp.base import AppContext
from resume_mcp.utils.latex import compile_latex
from resume_mcp.utils.llm import call_anthropic
from resume_mcp.utils.obsidian import save_obsidian_file


logger = logging.getLogger(__name__)


def parse_cv_response(response: str) -> Dict[str, str]:
    """
    Extract markdown and LaTeX content from an LLM response string.

    This function parses the response from a language model to extract CV content in markdown 
    and LaTeX formats. It first attempts to find content within markdown and LaTeX code blocks.
    If markdown content isn't found in a code block, it tries to identify CV-like content
    based on common section headers.

    Args:
        response (str): The raw string response from the language model

    Returns:
        Dict[str, str]: A dictionary with two keys:
            - "markdown": The extracted markdown content (empty string if none found)
            - "latex": The extracted LaTeX content (empty string if none found)

    Example:
        >>> result = parse_cv_response("```markdown\n# My CV\n```\n```latex\\documentclass{article}\\begin{document}CV\\end{document}```")
        >>> result["markdown"]
        '# My CV'
        >>> result["latex"]
        '\\documentclass{article}\\begin{document}CV\\end{document}'
    """
    """Extract markdown and LaTeX from LLM response"""
    result = {"markdown": "", "latex": ""}

    # Try to extract markdown CV
    markdown_match = re.search(
        r"```markdown\s*(.*?)\s*```", response, re.DOTALL)
    if markdown_match:
        result["markdown"] = markdown_match.group(1).strip()

    # Try to extract LaTeX CV
    latex_match = re.search(r"```latex\s*(.*?)\s*```", response, re.DOTALL)
    if latex_match:
        result["latex"] = latex_match.group(1).strip()

    # If structured format not found, try to find any code blocks
    if not result["markdown"]:
        # Look for any content that looks like a CV
        lines = response.split('\n')
        cv_content = []
        in_cv = False

        for line in lines:
            if any(marker in line.lower() for marker in ['# ', '## ', 'professional', 'experience', 'education']):
                in_cv = True
            if in_cv:
                cv_content.append(line)

        if cv_content:
            result["markdown"] = '\n'.join(cv_content)

    return result


def generate_cv_tailoring_prompt(
        company: str,
        position: str,
        app_ctx: AppContext,
        job_description: str = "") -> str:
    """
    Generate a prompt for tailoring a resume/CV to a specific job description.

    This function builds a tailored prompt by combining the baseline resume with job-specific details.
    It utilizes an application context to access resume and prompt management services.

    Args:
        job_description (str): The full text of the job description to tailor the resume for
        company (str): The name of the company the application is for
        position (str): The title of the position being applied for
        app_ctx (AppContext): Application context providing access to managers and services

    Returns:
        str: A complete prompt ready for submission to a language model for CV tailoring

    Example:
        prompt = generate_cv_tailoring_prompt(
            job_description="Looking for a Python developer with 5+ years...",
            company="TechCorp",
            position="Senior Developer",
            app_ctx=app_context
        )
    """

    resume_manager = app_ctx.resume_manager
    prompt_manager = app_ctx.prompt_manager

    baseline_resume = resume_manager.get_baseline_content()
    latex_template = prompt_manager.get_latex_template()

    prompt_variables = {
        "latex_template": latex_template,
        "baseline_resume": baseline_resume,
        "job_description": job_description,
        "company": company,
        "position": position
    }

    prompt = prompt_manager.substitute_variables(prompt_variables)

    return prompt


async def autogenerate_cv(job_description: str, company: str, position: str, app_ctx: AppContext) -> Dict:
    """
    Automate the generation of a tailored CV based on a job description.

    This asynchronous function processes a job description to create a customized curriculum
    vitae (CV) tailored for a specific position at a company, using an LLM to generate
    the content.

    Args:
        job_description (str): The job description text to tailor the CV for.
        company (str): The name of the company the position is at.
        position (str): The title of the position being applied for.
        app_ctx (AppContext): Application context containing user's profile data.

    Returns:
        Dict: A dictionary containing:
            - generated_files (list): Paths to all generated files
            - markdown_path (str, optional): Path to the generated markdown CV
            - pdf_path (str, optional): Path to the generated PDF CV if LaTeX compilation succeeded

    The function performs the following steps:
    1. Generate a tailoring prompt for the LLM
    2. Call the Anthropic LLM with the prompt
    3. Parse the LLM response to extract markdown and LaTeX content
    4. Save the content as markdown and (if available) compile LaTeX to PDF
    5. Save the raw LLM response for debugging purposes
    """

    logger.info(
        f"🚀 Starting automated CV generation for {position} at {company}")

    # Step 1: Generate the tailoring prompt
    logger.info("📝 Generating tailoring prompt...")
    prompt = generate_cv_tailoring_prompt(
        company, position, app_ctx, job_description=job_description)

    # Step 3: Call LLM with prompt
    logger.info("🤖 Executing prompt with LLM...")
    llm_response = await call_anthropic(prompt)

    # Step 4: Parse response
    logger.info("Parsing response...")
    parsed_content = parse_cv_response(llm_response)

    # Step 5: Save results
    results: Dict[str, Any] = {"generated_files": []}

    cv_name = f"{company} - {position}"

    # Save Markdown CV
    if "markdown" not in parsed_content:
        logger.warning("No markdown content found in LLM response")
    else:
        obsidian_filename = os.path.join(OUTPUT_DIRECTORY, f"{cv_name}.md")
        with open(obsidian_filename, mode="w", encoding="utf-8") as f:
            f.write(parsed_content["markdown"])
        results["markdown_path"] = obsidian_filename
        results["generated_files"].append(obsidian_filename)

    if "latex" in parsed_content:
        pdf_filename = os.path.join(OUTPUT_DIRECTORY, f"{cv_name}.pdf")
        # Save PDF
        compilation_result = compile_latex(
            content=parsed_content["latex"], dest=pdf_filename)
        if "error" in compilation_result:
            logger.warning(
                f"Failed to compile PDF, error: {compilation_result['error']}")
        elif "success" in compilation_result:
            pdf_dest = compilation_result["success"]["dest"]
            logger.info(
                f"Successfully saved PDF CV to:{pdf_dest}")
            results["pdf_path"] = pdf_dest
            results["generated_files"].append(pdf_dest)

    # Save raw LLM compilation response for debugging
    obsidian_filename = f"LLM/{company}_{position.replace(' ', '_')}_LLM_Response.md"

    response_filename = save_obsidian_file(
        content=f"# LLM Response for {company} - {position}\n\n```\n{llm_response}\n```",
        filename=obsidian_filename
    )

    results["generated_files"].append(response_filename)

    logger.info(f"✅ Automated CV generation completed!")
    logger.info(f"📁 Generated {len(results['generated_files'])} files")

    return results
