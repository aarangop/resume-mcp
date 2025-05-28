#!/usr/bin/env python3
"""
Integration tests for ResumeManager and PromptTemplateManager classes
Tests the classes with actual files as specified in the .env file
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open

import pytest

# Import from the refactored package structure
from resume_mcp.utils.resume_manager import ResumeManager
from resume_mcp.utils.prompt_manager import PromptTemplateManager
from resume_mcp.config import BASELINE_RESUME_PATH, PROMPT_TEMPLATE_PATH


# Fixtures for real files tests
@pytest.fixture
def setup_real_files():
    """Set up environment with resolved paths and sample files"""
    # Resolve environment variables and expand home directory (~)
    baseline_resume_path = os.path.expanduser(BASELINE_RESUME_PATH)
    prompt_template_path = os.path.expanduser(PROMPT_TEMPLATE_PATH)

    # Ensure test directories exist
    os.makedirs(os.path.dirname(baseline_resume_path), exist_ok=True)
    os.makedirs(os.path.dirname(prompt_template_path), exist_ok=True)

    # Sample content for test files
    sample_resume = "# John Doe Resume\n\n## Experience\n- Software Engineer at Example Corp"
    sample_template = "# Template\n\n## Resume:\n$baseline_resume\n\n## Job Description:\n$job_description"

    # Create test files if they don't exist
    if not os.path.exists(baseline_resume_path):
        with open(baseline_resume_path, 'w', encoding='utf-8') as f:
            f.write(sample_resume)

    if not os.path.exists(prompt_template_path):
        with open(prompt_template_path, 'w', encoding='utf-8') as f:
            f.write(sample_template)

    # Initialize managers with real paths
    resume_manager = ResumeManager(baseline_resume_path)
    prompt_manager = PromptTemplateManager(prompt_template_path)

    # Return all required objects as a dictionary
    return {
        "baseline_resume_path": baseline_resume_path,
        "prompt_template_path": prompt_template_path,
        "sample_resume": sample_resume,
        "sample_template": sample_template,
        "resume_manager": resume_manager,
        "prompt_manager": prompt_manager
    }


@pytest.fixture
def nonexistent_file():
    """Create a temporary file path that doesn't exist"""
    fd, path = tempfile.mkstemp()
    os.close(fd)
    os.unlink(path)  # Ensure the file doesn't exist
    yield path
    # No cleanup needed as the file doesn't exist


# Tests with real files
def test_resume_manager_init(setup_real_files):
    """Test ResumeManager initialization with real file"""
    resume_manager = setup_real_files["resume_manager"]
    baseline_resume_path = setup_real_files["baseline_resume_path"]

    assert resume_manager is not None
    assert resume_manager.resume_path == Path(baseline_resume_path)
    # Verify content was loaded
    assert resume_manager._baseline_content is not None


def test_resume_manager_get_content(setup_real_files):
    """Test ResumeManager.get_baseline_content with real file"""
    resume_manager = setup_real_files["resume_manager"]
    content = resume_manager.get_baseline_content()

    assert content is not None
    # Should contain content from the file, not the default message
    assert "No baseline resume found" not in content
    assert "Error loading baseline resume" not in content


def test_prompt_manager_init(setup_real_files):
    """Test PromptTemplateManager initialization with real file"""
    prompt_manager = setup_real_files["prompt_manager"]
    prompt_template_path = setup_real_files["prompt_template_path"]

    assert prompt_manager is not None
    assert prompt_manager.template_path == Path(prompt_template_path)
    # Verify content was loaded
    assert prompt_manager._template_content is not None


def test_variable_substitution(setup_real_files):
    """Test variable substitution in the template"""
    prompt_manager = setup_real_files["prompt_manager"]
    variables = {
        "baseline_resume": "My test resume",
        "job_description": "Sample job description"
    }

    result = prompt_manager.substitute_variables(variables)
    assert "My test resume" in result
    assert "Sample job description" in result


def test_reload_functions(setup_real_files):
    """Test reload functions for both managers"""
    resume_manager = setup_real_files["resume_manager"]
    prompt_manager = setup_real_files["prompt_manager"]
    baseline_resume_path = setup_real_files["baseline_resume_path"]
    prompt_template_path = setup_real_files["prompt_template_path"]

    # First modify the files
    with open(baseline_resume_path, 'a', encoding='utf-8') as f:
        f.write("\n- Updated resume content")

    with open(prompt_template_path, 'a', encoding='utf-8') as f:
        f.write("\n\n## Updated template section")

    # Reload from files
    resume_manager.reload_baseline()
    prompt_manager.reload_templates()

    # Check updated content was loaded
    assert "Updated resume content" in resume_manager.get_baseline_content()
    result = prompt_manager.substitute_variables(
        {"baseline_resume": "resume", "job_description": "job"})
    assert "Updated template section" in result


# Tests with missing files
def test_missing_resume_file(nonexistent_file):
    """Test ResumeManager behavior when file is missing"""
    manager = ResumeManager(nonexistent_file)
    content = manager.get_baseline_content()
    assert "No baseline resume found" in content


def test_resume_reload_with_missing_file(nonexistent_file):
    """Test reload behavior with missing file"""
    manager = ResumeManager(nonexistent_file)
    # Initial state has the default message
    assert "No baseline resume found" in manager.get_baseline_content()

    # Now create the file
    with open(nonexistent_file, 'w', encoding='utf-8') as f:
        f.write("New resume content")

    # Reload and check content
    manager.reload_baseline()
    assert manager.get_baseline_content() == "New resume content"

    # Clean up
    os.unlink(nonexistent_file)


def test_missing_template_file(nonexistent_file):
    """Test PromptTemplateManager behavior when file is missing"""
    manager = PromptTemplateManager(nonexistent_file)
    variables = {"baseline_resume": "resume", "job_description": "job"}
    content = manager.substitute_variables(variables)
    # Should use default template
    assert "CRITICAL CONSTRAINTS" in content
    assert "resume" in content
    assert "job" in content


def test_template_reload_with_missing_file(nonexistent_file):
    """Test reload behavior with missing file"""
    manager = PromptTemplateManager(nonexistent_file)
    # Initial state has the default template

    # Now create the file
    with open(nonexistent_file, 'w', encoding='utf-8') as f:
        f.write("Custom template: $baseline_resume / $job_description")

    # Reload and check content
    manager.reload_templates()
    result = manager.substitute_variables(
        {"baseline_resume": "resume", "job_description": "job"})
    assert result == "Custom template: resume / job"

    # Clean up
    os.unlink(nonexistent_file)


# Error case tests
def test_resume_manager_general_error():
    """Test ResumeManager behavior with general errors"""
    with patch('builtins.open', side_effect=Exception("Test error")):
        manager = ResumeManager("some/path.md")
        content = manager.get_baseline_content()
        assert content == "Error loading baseline resume."


def test_prompt_manager_general_error():
    """Test PromptTemplateManager behavior with general errors"""
    with patch('builtins.open', side_effect=Exception("Test error")):
        manager = PromptTemplateManager("some/path.md")
        if manager._template_content:
            # Should use default template
            assert "CRITICAL CONSTRAINTS" in manager._template_content
        assert False, "No template content in PromptTemplateManager"


def test_invalid_template_variables():
    """Test error handling with invalid template variables"""
    # Create a template with syntax error
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        f.write("Template with $invalid syntax ${")
        temp_path = f.name

    # Create manager with problematic template
    manager = PromptTemplateManager(temp_path)

    # This should raise an exception
    with pytest.raises(Exception):
        manager.substitute_variables(
            {"baseline_resume": "resume", "job_description": "job"})

    # Clean up
    os.unlink(temp_path)
