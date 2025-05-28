
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
    prompt_name: str,
) -> str:

    app_ctx = get_app_context()
    tailored_prompt = gen_cv_prompt(
        company,
        position,
        app_ctx,
        job_description=job_description
    )
    output_file = os.path.join(OBSIDIAN_VAULT, "prompts", f"{prompt_name}.md")
    with open(output_file, mode='+w') as f:
        f.write(tailored_prompt)
    return f"✅ Prompt successfully saved prompt to '{output_file}'"


@mcp.tool(name="generate_tailored_cv", description="Fully automatic generation of a CV and further materials based on a job description")
async def generate_tailored_cv(job_description: str, company: str, position: str):
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
