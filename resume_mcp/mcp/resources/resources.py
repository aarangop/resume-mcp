from typing import cast
from resume_mcp.mcp.base import AppContext, mcp


@mcp.resource("file://files/base-cv", name="Base CV")
def base_cv() -> str:
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)
    baseline_resume = app_ctx.resume_manager.get_baseline_content()
    return baseline_resume


@mcp.resource("file://files/latex_template", name="LaTeX Template")
def latex_template():
    ctx = mcp.get_context()
    app_ctx = cast(AppContext, ctx.request_context.lifespan_context)
    latex_template = app_ctx.prompt_manager.get_latex_template()
    return latex_template
