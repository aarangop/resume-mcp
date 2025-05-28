"""
Unit tests for CV utility functions
"""

import os
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import re

from resume_mcp.mcp.base import AppContext
from resume_mcp.utils.cv import (
    parse_cv_response,
    generate_cv_tailoring_prompt,
    autogenerate_cv
)
from resume_mcp.utils.prompt_manager import PromptTemplateManager
from resume_mcp.utils.resume_manager import ResumeManager


class TestParseResponse:
    """Tests for parse_cv_response function"""

    def test_parse_markdown_only(self):
        """Test parsing with only markdown content"""
        response = """
        Here's your CV: 
        
        ```markdown
        # John Doe
        
        ## Experience
        - Software Engineer
        ```
        """
        result = parse_cv_response(response)
        assert "markdown" in result
        assert "# John Doe" in result["markdown"]
        assert "latex" in result
        assert result["latex"] == ""

    def test_parse_latex_only(self):
        """Test parsing with only LaTeX content"""
        response = """
        Here's your CV: 
        
        ```latex
        \\documentclass{article}
        
        \\begin{document}
        John Doe
        \\end{document}
        ```
        """
        result = parse_cv_response(response)
        assert "markdown" in result
        assert result["markdown"] == ""
        assert "latex" in result
        assert "\\documentclass{article}" in result["latex"]

    def test_parse_both_formats(self):
        """Test parsing with both markdown and LaTeX content"""
        response = """
        Here's your CV: 
        
        ```markdown
        # John Doe
        
        ## Experience
        - Software Engineer
        ```
        
        And here's the LaTeX version:
        
        ```latex
        \\documentclass{article}
        
        \\begin{document}
        John Doe
        \\end{document}
        ```
        """
        result = parse_cv_response(response)
        assert "markdown" in result
        assert "# John Doe" in result["markdown"]
        assert "latex" in result
        assert "\\documentclass{article}" in result["latex"]

    def test_parse_unstructured_response(self):
        """Test parsing unstructured response"""
        response = """
        # John Doe
        
        ## Experience
        - Software Engineer
        
        ## Education
        - University
        """
        result = parse_cv_response(response)
        assert "markdown" in result
        assert "# John Doe" in result["markdown"]
        assert "latex" in result
        assert result["latex"] == ""

    def test_parse_empty_response(self):
        """Test parsing empty response"""
        response = ""
        result = parse_cv_response(response)
        assert "markdown" in result
        assert result["markdown"] == ""
        assert "latex" in result
        assert result["latex"] == ""


@pytest.fixture
def mock_app_context():
    """Create a mock AppContext for testing"""
    mock_resume_manager = MagicMock(spec=ResumeManager)
    mock_resume_manager.get_baseline_content.return_value = "# My Resume\n\n## Experience\nSoftware Engineer"

    mock_prompt_manager = MagicMock(spec=PromptTemplateManager)
    mock_prompt_manager.get_latex_template.return_value = "\\documentclass{article}"
    mock_prompt_manager.substitute_variables.return_value = "Test prompt with variable substitution"

    return AppContext(
        prompt_manager=mock_prompt_manager,
        resume_manager=mock_resume_manager,
        output_directory=Path("tests/test_output")
    )


class TestPromptGeneration:
    """Tests for generate_cv_tailoring_prompt function"""

    def test_generate_tailoring_prompt(self, mock_app_context):
        """Test generation of tailoring prompt"""
        job_description = "Looking for a Python developer"
        company = "TechCorp"
        position = "Senior Developer"

        result = generate_cv_tailoring_prompt(
            job_description=job_description,
            company=company,
            position=position,
            app_ctx=mock_app_context
        )

        # Assert resume manager was called to get baseline content
        mock_app_context.resume_manager.get_baseline_content.assert_called_once()

        # Assert prompt manager was called to get LaTeX template
        mock_app_context.prompt_manager.get_latex_template.assert_called_once()

        # Assert variables were substituted correctly
        mock_app_context.prompt_manager.substitute_variables.assert_called_once()
        called_with = mock_app_context.prompt_manager.substitute_variables.call_args[0][0]
        assert called_with["latex_template"] == "\\documentclass{article}"
        assert called_with["baseline_resume"] == "# My Resume\n\n## Experience\nSoftware Engineer"
        assert called_with["job_description"] == "Looking for a Python developer"
        assert called_with["company"] == "TechCorp"
        assert called_with["position"] == "Senior Developer"

        # Assert the function returns the prompt
        assert result == "Test prompt with variable substitution"


@pytest.fixture
def mock_files_cleanup():
    """Clean up test files after tests"""
    yield
    # Clean up any files created during testing
    test_files = [
        os.path.join("test_output", "TestCorp - Developer.md"),
        os.path.join("test_output", "TestCorp - Developer.pdf")
    ]
    for file in test_files:
        if os.path.exists(file):
            os.remove(file)

    # Ensure the directory exists for tests
    os.makedirs("test_output", exist_ok=True)


class TestAutogenerateCv:
    """Tests for autogenerate_cv function"""

    @pytest.mark.asyncio
    @patch("resume_mcp.utils.cv.call_anthropic", new_callable=AsyncMock)
    @patch("resume_mcp.utils.cv.compile_latex")
    @patch("resume_mcp.utils.cv.save_obsidian_file")
    async def test_autogenerate_cv_success(self, mock_save_obsidian, mock_compile_latex,
                                           mock_call_anthropic, mock_app_context,
                                           mock_files_cleanup):
        """Test successful CV generation with both markdown and LaTeX output"""
        # Setup the mock returns
        mock_call_anthropic.return_value = """
        ```markdown
        # Test CV
        ## Experience
        - Developer
        ```
        
        ```latex
        \\documentclass{article}
        \\begin{document}
        Test CV
        \\end{document}
        ```
        """

        # Setup LaTeX compilation success
        mock_compile_latex.return_value = {
            "success": {"dest": os.path.join("test_output", "TestCorp - Developer.pdf")}
        }

        # Setup obsidian file save
        mock_save_obsidian.return_value = "test/obsidian/response.md"

        # Set output directory in app context
        mock_app_context.output_directory = "test_output"

        # Call the function
        result = await autogenerate_cv(
            job_description="Looking for a developer",
            company="TestCorp",
            position="Developer",
            app_ctx=mock_app_context
        )

        # Verify call to LLM
        mock_call_anthropic.assert_called_once()

        # Verify LaTeX compilation
        mock_compile_latex.assert_called_once()

        # Check result contents
        assert "generated_files" in result
        assert len(result["generated_files"]) == 3
        assert "markdown_path" in result
        assert "pdf_path" in result
        assert result["pdf_path"] == os.path.join(
            "test_output", "TestCorp - Developer.pdf")

    @pytest.mark.asyncio
    @patch("resume_mcp.utils.cv.call_anthropic", new_callable=AsyncMock)
    @patch("resume_mcp.utils.cv.compile_latex")
    @patch("resume_mcp.utils.cv.save_obsidian_file")
    async def test_autogenerate_cv_latex_failure(self, mock_save_obsidian, mock_compile_latex,
                                                 mock_call_anthropic, mock_app_context,
                                                 mock_files_cleanup):
        """Test CV generation with LaTeX compilation failure"""
        # Setup the mock returns
        mock_call_anthropic.return_value = """
        ```markdown
        # Test CV
        ## Experience
        - Developer
        ```
        
        ```latex
        \\documentclass{article}
        \\begin{document}
        Test CV with errors
        \\end{document}
        ```
        """

        # Setup LaTeX compilation failure
        mock_compile_latex.return_value = {
            "error": "LaTeX compilation failed"
        }

        # Setup obsidian file save
        mock_save_obsidian.return_value = "test/obsidian/response.md"

        # Set output directory in app context
        mock_app_context.output_directory = "test_output"

        # Call the function
        result = await autogenerate_cv(
            job_description="Looking for a developer",
            company="TestCorp",
            position="Developer",
            app_ctx=mock_app_context
        )

        # Check result contents
        assert "generated_files" in result
        # Only markdown file and raw response
        assert len(result["generated_files"]) == 2
        assert "markdown_path" in result
        assert "pdf_path" not in result

    @pytest.mark.asyncio
    @patch("resume_mcp.utils.cv.call_anthropic", new_callable=AsyncMock)
    @patch("resume_mcp.utils.cv.save_obsidian_file")
    async def test_autogenerate_cv_markdown_only(self, mock_save_obsidian,
                                                 mock_call_anthropic, mock_app_context,
                                                 mock_files_cleanup):
        """Test CV generation with only markdown (no LaTeX)"""
        # Setup the mock returns
        mock_call_anthropic.return_value = """
        ```markdown
        # Test CV
        ## Experience
        - Developer
        ```
        """

        # Setup obsidian file save
        mock_save_obsidian.return_value = "test/obsidian/response.md"

        # Set output directory in app context
        mock_app_context.output_directory = "test_output"

        # Call the function
        result = await autogenerate_cv(
            job_description="Looking for a developer",
            company="TestCorp",
            position="Developer",
            app_ctx=mock_app_context
        )

        # Check result contents
        assert "generated_files" in result
        # Only markdown file and raw response
        assert len(result["generated_files"]) == 2
        assert "markdown_path" in result
        assert "pdf_path" not in result


if __name__ == "__main__":
    pytest.main(["-v", "test_cv.py"])
