"""
Validation Tools Module
"""

import logging
import sys
import os

from resume_mcp.utils.latex import check_pdflatex

from ..base import mcp, get_app_context

logger = logging.getLogger(__name__)


@mcp.tool()
def validate_configuration() -> str:
    """
    Validate that all required files and configurations are properly set up.

    Returns:
        Validation report with recommendations
    """
    try:
        # Get app context
        app_ctx = get_app_context()

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

        # Check prompt template
        if not app_ctx.prompt_manager.template_path.exists():
            issues.append("❌ Prompt template file not found")
            recommendations.append("Template will use built-in default")

        # Check LaTeX template
        if app_ctx.prompt_manager.latex_template_path:
            if not app_ctx.prompt_manager.latex_template_path.exists():
                issues.append("❌ LaTeX template file not found")
                recommendations.append(
                    "Create LaTeX template for PDF generation")
            else:
                is_valid, message = app_ctx.prompt_manager.validate_latex_template()
                if not is_valid:
                    issues.append(f"⚠️ LaTeX template issue: {message}")
                    recommendations.append("Fix LaTeX template placeholders")

        # Check output directories
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


@mcp.tool()
def debug_resources() -> str:
    """
    Debug information about loaded resources and Obsidian configuration.

    Returns:
        Debug information about resources
    """
    try:
        from ...config import OBSIDIAN_VAULT
        from pathlib import Path

        vault_path = Path(OBSIDIAN_VAULT)

        debug_info = f"""# Resource Debug Information

## Obsidian Configuration
- **Vault Path:** {OBSIDIAN_VAULT}
- **Path Exists:** {'✅ Yes' if vault_path.exists() else '❌ No'}
- **Is Directory:** {'✅ Yes' if vault_path.is_dir() else '❌ No'}

"""

        if vault_path.exists() and vault_path.is_dir():
            # Count markdown files
            md_files = list(vault_path.rglob("*.md"))
            debug_info += f"""## Vault Contents
- **Total .md files:** {len(md_files)}
- **Sample files:** {', '.join([f.name for f in md_files[:5]])}
"""

        # Try to access the MCP server context to see registered resources
        try:
            ctx = mcp.get_context()
            debug_info += f"""
## MCP Context
- **Context Available:** ✅ Yes
- **Request Context:** {hasattr(ctx, 'request_context')}
"""
        except Exception as e:
            debug_info += f"""
## MCP Context
- **Context Available:** ❌ No - {str(e)}
"""

        debug_info += f"""
## Available Resources
To test your Obsidian resources, try:
- obsidian://list_files - List all files in vault
- obsidian://job_description/engineer - Search for files matching 'engineer'
- obsidian://file/filename - Get specific file content

## Troubleshooting
1. Ensure OBSIDIAN_VAULT environment variable is set
2. Check that the vault path exists and contains .md files  
3. Restart the MCP server after configuration changes
4. Check the MCP Inspector or Claude Desktop for available resources
"""

        return debug_info

    except Exception as e:
        return f"❌ Error getting resource debug info: {str(e)}"


@mcp.tool(name="check_pdflatex", description="Checks whether pdflatex is installed on the user's system")
def check_pdflatex_tool() -> bool:
    return check_pdflatex()


@mcp.tool(name="check_latex_server", description="Checks if the LaTeX compilation server is available")
def check_latex_server_tool():
    """
    Check if the containerized LaTeX compilation server is running and healthy.

    Returns:
        Dictionary with server health status information including:
        - available: whether the server is running
        - message: status message
        - details: additional server information (if available)
    """
    from resume_mcp.utils.latex import check_latex_server
    return check_latex_server()
