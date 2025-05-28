import os
import pytest
import shutil
import subprocess
from pathlib import Path

from resume_mcp.utils.latex import compile_latex


@pytest.fixture
def test_paths():
    """Setup test directories and paths."""
    test_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    test_data_dir = test_dir / "test_data"
    test_output_dir = test_dir / "test_output"

    # Create output directory if it doesn't exist
    test_output_dir.mkdir(exist_ok=True)

    return {
        "test_dir": test_dir,
        "test_data_dir": test_data_dir,
        "test_output_dir": test_output_dir,
        "test_cv_path": test_data_dir / "test_cv.tex"
    }


@pytest.fixture(scope="session", autouse=True)
def check_pdflatex():
    """Check if pdflatex is installed in the system."""
    pdflatex_path = shutil.which("pdflatex")
    if not pdflatex_path:
        pytest.skip(
            "pdflatex is not installed in the system, skipping LaTeX tests")

    # Check pdflatex version to make sure it's working
    try:
        result = subprocess.run(["pdflatex", "--version"],
                                capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            pytest.skip(
                "pdflatex is installed but not working correctly, skipping LaTeX tests")
    except subprocess.TimeoutExpired:
        pytest.skip("pdflatex command timed out, skipping LaTeX tests")
    except Exception as e:
        pytest.skip(f"Error checking pdflatex: {e}, skipping LaTeX tests")

    return pdflatex_path


def test_compile_latex(test_paths):
    """Test that the LaTeX compilation works correctly with a sample CV file."""
    # Read the test CV file
    with open(test_paths["test_cv_path"], "r", encoding="utf-8") as f:
        latex_content = f.read()

    # Define output path for the compiled PDF
    output_pdf_path = str(
        test_paths["test_output_dir"] / "test_compiled_cv.pdf")

    # Compile the LaTeX to PDF
    result = compile_latex(latex_content, output_pdf_path)

    # Check that compilation was successful
    assert "success" in result, f"LaTeX compilation failed: {result.get('error', 'Unknown error')}"
    assert result["success"]["dest"] == output_pdf_path

    # Check that the PDF file was actually created
    assert os.path.exists(
        output_pdf_path), f"PDF file was not created at {output_pdf_path}"
    assert os.path.getsize(output_pdf_path) > 0, "PDF file is empty"


def test_compile_latex_temp_dir_handling(test_paths):
    """Test that the LaTeX compilation properly handles temporary directories."""
    # Read the test CV file
    with open(test_paths["test_cv_path"], "r", encoding="utf-8") as f:
        latex_content = f.read()

    # Define output path for the compiled PDF
    output_pdf_path = str(
        test_paths["test_output_dir"] / "test_temp_dir_handling.pdf")

    # Compile the LaTeX to PDF
    result = compile_latex(latex_content, output_pdf_path)

    # Check that compilation was successful
    assert "success" in result, f"LaTeX compilation failed: {result.get('error', 'Unknown error')}"

    # Check that the PDF file was actually created
    assert os.path.exists(
        output_pdf_path), f"PDF file was not created at {output_pdf_path}"


def test_compile_latex_error_handling():
    """Test that the LaTeX compilation properly handles errors."""
    # Create intentionally invalid LaTeX content
    invalid_latex_content = r"""
    \documentclass{article}
    \begin{document}
    \undefinedcommand  % This command doesn't exist and will cause an error
    \end{document}
    """

    # Define output path for the compiled PDF
    output_dir = Path(os.path.dirname(
        os.path.abspath(__file__))) / "test_output"
    output_dir.mkdir(exist_ok=True)
    output_pdf_path = str(output_dir / "test_error_handling.pdf")

    # Compile the invalid LaTeX
    result = compile_latex(invalid_latex_content, output_pdf_path)

    # Check that compilation failed as expected
    assert "error" in result, "LaTeX compilation should have failed but succeeded"
    assert "LaTeX compilation failed" in result["error"], "Error message doesn't indicate LaTeX compilation failure"

    # The PDF file should not exist
    assert not os.path.exists(
        output_pdf_path), "PDF file was created despite LaTeX errors"
