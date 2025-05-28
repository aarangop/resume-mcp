"""
Management Tools Module
"""

import logging
import subprocess
from pathlib import Path

from ..base import mcp, get_app_context
from ...config import LATEX_OUTPUT_DIR, SERVER_NAME

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
        app_ctx = get_app_context()

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
        app_ctx = get_app_context()

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


@mcp.tool()
def validate_latex_setup() -> str:
    """
    Validate LaTeX template and compilation setup.

    Returns:
        Validation report for LaTeX configuration
    """
    try:
        app_ctx = get_app_context()

        report = "# LaTeX Setup Validation\n\n"

        # Check template
        is_valid, message = app_ctx.prompt_manager.validate_latex_template()
        report += f"## Template Status: {'✅ Valid' if is_valid else '❌ Invalid'}\n"
        report += f"- {message}\n\n"

        # Check LaTeX installation
        try:
            result = subprocess.run(['pdflatex', '--version'],
                                    capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                report += "## LaTeX Installation: ✅ Found\n"
                report += f"- Version: {result.stdout.split()[0]} available\n\n"
            else:
                report += "## LaTeX Installation: ❌ Not Working\n\n"
        except (subprocess.TimeoutExpired, FileNotFoundError):
            report += "## LaTeX Installation: ❌ Not Found\n"
            report += "- Install LaTeX (TeX Live, MiKTeX, or MacTeX) to compile PDFs\n\n"

        # Check directories
        latex_dir = Path(LATEX_OUTPUT_DIR)
        report += f"## Output Directory: {'✅ Ready' if latex_dir.exists() else '❌ Missing'}\n"
        report += f"- LaTeX Output: {latex_dir}\n\n"

        # Template info
        latex_template = app_ctx.prompt_manager.get_latex_template()
        if latex_template:
            template_size = len(latex_template)
            report += f"## Template Info:\n"
            report += f"- Size: {template_size} characters\n"
            report += f"- Path: {app_ctx.prompt_manager.latex_template_path}\n"

        return report

    except Exception as e:
        return f"❌ Error validating LaTeX setup: {str(e)}"


@mcp.tool()
def get_latex_template_info() -> str:
    """
    Get information about the current LaTeX template.

    Returns:
        LaTeX template details and structure
    """
    try:
        app_ctx = get_app_context()

        latex_template = app_ctx.prompt_manager.get_latex_template()
        if not latex_template:
            return "❌ No LaTeX template loaded"

        # Extract placeholders
        import re
        placeholders = re.findall(r'\$\w+', latex_template)
        unique_placeholders = sorted(set(placeholders))

        return f"""# LaTeX Template Information

## Template Path
{app_ctx.prompt_manager.latex_template_path}

## Template Size
{len(latex_template)} characters

## Available Placeholders
{chr(10).join(f'- {p}' for p in unique_placeholders)}

## Template Preview (First 500 characters)
```latex
{latex_template[:500]}{'...' if len(latex_template) > 500 else ''}
```

## Usage
Use the `tailor_resume_dual_format` or `latex_only_tailor` prompts to generate 
tailored LaTeX CVs using this template.
"""

    except Exception as e:
        return f"❌ Error getting LaTeX template info: {str(e)}"
