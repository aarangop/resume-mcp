from pathlib import Path
from typing import cast
from resume_mcp.config import LATEX_OUTPUT_DIR
from resume_mcp.mcp.base import AppContext, mcp


@mcp.tool()
def validate_latex_setup() -> str:
    """
    Validate LaTeX template and compilation setup.

    Returns:
        Validation report for LaTeX configuration
    """
    try:
        ctx = mcp.get_context()
        app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

        report = "# LaTeX Setup Validation\n\n"

        # Check template
        is_valid, message = app_ctx.prompt_manager.validate_latex_template()
        report += f"## Template Status: {'✅ Valid' if is_valid else '❌ Invalid'}\n"
        report += f"- {message}\n\n"

        # Check LaTeX installation
        import subprocess
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
        ctx = mcp.get_context()
        app_ctx = cast(AppContext, ctx.request_context.lifespan_context)

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
