import logging
from typing import cast
from resume_mcp.config import LATEX_OUTPUT_DIR, SERVER_NAME
from resume_mcp.mcp.base import AppContext, mcp

# Configure logger
logger = logging.getLogger(__name__)


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

        app_ctx.prompt_manager.reload_templates()
        app_ctx.resume_manager.reload_baseline()

        logger.info("Templates reloaded successfully")
        return "✅ Successfully reloaded prompt template, LaTeX template, and baseline resume from files"
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
        latex_template_exists = (app_ctx.prompt_manager.latex_template_path and
                                 app_ctx.prompt_manager.latex_template_path.exists())

        # Get some basic stats
        baseline_length = len(app_ctx.resume_manager.get_baseline_content())
        latex_template_length = len(
            app_ctx.prompt_manager.get_latex_template() or "")

        return f"""# Resume Tailoring Server Status

## Configuration
- **Server Name:** {SERVER_NAME}
- **Baseline Resume Path:** {app_ctx.resume_manager.resume_path}
- **Prompt Template Path:** {app_ctx.prompt_manager.template_path}
- **LaTeX Template Path:** {app_ctx.prompt_manager.latex_template_path or 'Not configured'}
- **Output Directory:** {app_ctx.output_directory}
- **LaTeX Output Directory:** {LATEX_OUTPUT_DIR}

## File Status
- **Baseline Resume:** {'✅ Found' if resume_exists else '❌ Not Found'}
- **Prompt Template:** {'✅ Found' if template_exists else '❌ Not Found'}
- **LaTeX Template:** {'✅ Found' if latex_template_exists else '❌ Not Found'}
- **Output Directory:** {'✅ Ready' if app_ctx.output_directory.exists() else '❌ Not Found'}

## Content Stats
- **Baseline Resume Length:** {baseline_length} characters
- **LaTeX Template Length:** {latex_template_length} characters

## Available Prompts
- **tailor_resume** - Full-featured resume tailoring (Markdown output)
- **tailor_resume_dual_format** - 🆕 Dual Markdown + LaTeX output
- **latex_only_tailor** - 🆕 LaTeX-focused resume tailoring
- **quick_tailor** - Streamlined resume tailoring
- **analyze_job_fit** - Job fit analysis
- **cover_letter_prompt** - Cover letter generation
- **interview_prep** - Interview preparation guidance

## Available Tools
- **reload_templates** - Refresh files from disk
- **get_server_status** - This status information
- **validate_latex_setup** - 🆕 Check LaTeX installation and template
- **get_latex_template_info** - 🆕 LaTeX template details
- **validate_configuration** - Configuration validation
- **debug_transport_info** - Transport debugging information

## Usage
Use the prompts directly in your MCP client. For LaTeX output, use:
- `tailor_resume_dual_format` for both Markdown and LaTeX
- `latex_only_tailor` for pure LaTeX output
"""
    except Exception as e:
        error_msg = f"❌ Error getting server status: {str(e)}"
        logger.error(error_msg)
        return error_msg
