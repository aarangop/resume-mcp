import os
import pytest
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock

from resume_mcp.utils.latex import compile_latex, check_latex_server, compile_latex_http
from resume_mcp.config import LATEX_SERVER_URL


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
def check_latex_server_available():
    """Check if LaTeX server is available."""
    # If testing with mocks is enabled, skip the actual server check
    if os.environ.get("MOCK_LATEX_SERVER") == "1":
        return {"available": True, "details": {"pdflatex_available": True}}

    # Otherwise check the real server
    server_status = check_latex_server()
    if not server_status["available"]:
        pytest.skip(
            f"LaTeX server is not available: {server_status['message']}. Please start the LaTeX server with: docker-compose up -d")

    # Check if pdflatex is available on the server
    if not server_status["details"].get("pdflatex_available", False):
        pytest.skip(
            "pdflatex is not available on the LaTeX server. Check server configuration.")

    return server_status


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


def test_check_latex_server():
    """Test that check_latex_server correctly reports the server status."""
    server_status = check_latex_server()
    assert isinstance(server_status, dict)
    assert "available" in server_status
    assert "message" in server_status
    assert "details" in server_status


@pytest.mark.parametrize(
    "status_code,expected_available",
    [
        (200, True),
        (500, False),
        (404, False),
    ],
)
def test_check_latex_server_response_handling(status_code, expected_available):
    """Test that check_latex_server correctly handles different server responses."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    if status_code == 200:
        mock_response.json.return_value = {"pdflatex_available": True}

    with patch("requests.get", return_value=mock_response):
        server_status = check_latex_server()
        assert server_status["available"] == expected_available


def test_check_latex_server_connection_error():
    """Test that check_latex_server correctly handles connection errors."""
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError("Connection error")):
        server_status = check_latex_server()
        assert not server_status["available"]
        assert "LaTeX server is not running" in server_status["message"]


@pytest.mark.parametrize(
    "server_response,expected_result_key",
    [
        ({"status_code": 200, "content": b"mock pdf content"}, "success"),
        ({"status_code": 500, "text": "Server error",
         "json": lambda: {"detail": "Compilation error"}}, "error"),
    ],
)
def test_compile_latex_http_response_handling(server_response, expected_result_key):
    """Test that compile_latex_http correctly handles different server responses."""
    mock_response = MagicMock()
    mock_response.status_code = server_response["status_code"]

    if "content" in server_response:
        mock_response.content = server_response["content"]

    if "text" in server_response:
        mock_response.text = server_response["text"]

    if "json" in server_response:
        mock_response.json = server_response["json"]

    server_status = {"available": True,
                     "details": {"pdflatex_available": True}}

    with patch("resume_mcp.utils.latex.check_latex_server", return_value=server_status), \
            patch("requests.post", return_value=mock_response), \
            patch("builtins.open", MagicMock()), \
            patch("os.path.exists", return_value=True):

        result = compile_latex_http("mock latex content", "/tmp/output.pdf")
        assert expected_result_key in result


def test_compile_latex_http_server_unavailable():
    """Test that compile_latex_http handles when the server is unavailable."""
    server_status = {"available": False,
                     "message": "Server offline", "details": {}}

    with patch("resume_mcp.utils.latex.check_latex_server", return_value=server_status):
        result = compile_latex_http("mock latex content", "/tmp/output.pdf")
        assert "error" in result
        assert "Server offline" in result["error"]


def test_compile_latex_http_server_no_pdflatex():
    """Test that compile_latex_http handles when pdflatex is not available on the server."""
    server_status = {"available": True,
                     "details": {"pdflatex_available": False}}

    with patch("resume_mcp.utils.latex.check_latex_server", return_value=server_status):
        result = compile_latex_http("mock latex content", "/tmp/output.pdf")
        assert "error" in result
        assert "pdflatex is not available" in result["error"]


def test_compile_latex_http_request_exception():
    """Test that compile_latex_http handles request exceptions."""
    server_status = {"available": True,
                     "details": {"pdflatex_available": True}}

    with patch("resume_mcp.utils.latex.check_latex_server", return_value=server_status), \
            patch("requests.post", side_effect=requests.exceptions.RequestException("Network error")):

        result = compile_latex_http("mock latex content", "/tmp/output.pdf")
        assert "error" in result
        assert "Network error" in result["error"]


def test_compile_latex_http_timeout():
    """Test that compile_latex_http handles timeouts."""
    server_status = {"available": True,
                     "details": {"pdflatex_available": True}}

    with patch("resume_mcp.utils.latex.check_latex_server", return_value=server_status), \
            patch("requests.post", side_effect=requests.exceptions.Timeout("Timeout")):

        result = compile_latex_http("mock latex content", "/tmp/output.pdf")
        assert "error" in result
        assert "timed out" in result["error"]
