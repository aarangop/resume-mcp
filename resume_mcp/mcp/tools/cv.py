
import os
from typing import Optional

from resume_mcp.config import OBSIDIAN_VAULT
from resume_mcp.utils.cv import autogenerate_cv, generate_cv_tailoring_prompt as gen_cv_prompt
from ..base import get_app_context, mcp


@mcp.tool(
    name="generate_cv_prompt",
    description="Generates and saves a CV tailoring prompt in the Obsidian Vault")
def generate_cv_tailoring_prompt(
        job_description: str,
        company: str,
        position: str,
        prompt_name: str) -> str:
    """
    Generate a prompt for creating a tailored CV based on job description and company details.

    This function creates a customized prompt for CV generation tailored to a specific job
    and company, then saves it to a file in the user's vault's prompts directory.

    Parameters
    ----------
    job_description : str
        The full job description text
    company : str
        The name of the company offering the position
    position : str
        The job title or position name
    prompt_name : str
        The name to use for the saved prompt file (without extension)

    Returns
    -------
    str
        A success message confirming where the prompt was saved

    Notes
    -----
    The function uses the application context to generate the CV prompt and
    saves it to the configured Obsidian vault location.
    """
    app_ctx = get_app_context()
    tailored_prompt = gen_cv_prompt(
        company,
        position,
        app_ctx,
        job_description=job_description
    )
    prompt_dir = os.path.join(OBSIDIAN_VAULT, "prompts")
    if not os.path.exists(prompt_dir):
        raise Exception(
            f"Prompt directory '{prompt_dir}' does not exist, please create it before using this tool.")
    output_file = os.path.join(OBSIDIAN_VAULT, "prompts", f"{prompt_name}.md")
    with open(output_file, mode='+w') as f:
        f.write(tailored_prompt)
    return f"✅ Prompt successfully saved prompt to '{output_file}'"


@mcp.tool(
    name="generate_tailored_cv",
    description="Fully automatic generation of a CV and further materials based on a job description. WARNING: Uses Anthropic API Key and might incur costs.")
async def generate_tailored_cv(job_description: str, company: str, position: str):
    """
    Generate a tailored CV based on job description, company, and position.

    This asynchronous function processes the input parameters and utilizes the autogenerate_cv
    function to create a customized CV document.

    Args:
        job_description (str): The job description text to tailor the CV against
        company (str): The name of the company the CV is being tailored for
        position (str): The position title being applied for

    Returns:
        dict or Exception: The results from the CV autogeneration process if successful,
                          or the exception object if an error occurred during processing

    Raises:
        No exceptions are directly raised by this function, as it catches and returns any
        exceptions from the autogenerate_cv function
    """
    app_ctx = get_app_context()
    try:
        cv_autogen_results = await autogenerate_cv(
            job_description=job_description,
            company=company,
            position=position,
            app_ctx=app_ctx
        )
    except Exception as e:
        return e

    return cv_autogen_results
