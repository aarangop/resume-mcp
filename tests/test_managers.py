#!/usr/bin/env python3
"""
Integration tests for ResumeManager and PromptTemplateManager classes
Tests the classes with actual files as specified in the .env file
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

# Import from the refactored package structure
from resume_mcp.utils.resume_manager import ResumeManager
from resume_mcp.utils.prompt_manager import PromptTemplateManager
from resume_mcp.config import BASELINE_RESUME_PATH, PROMPT_TEMPLATE_PATH


class TestManagersWithRealFiles(unittest.TestCase):
    """Test ResumeManager and PromptTemplateManager with real files from .env"""

    def setUp(self):
        """Set up test environment with resolved paths"""
        # Resolve environment variables and expand home directory (~)
        self.baseline_resume_path = os.path.expanduser(BASELINE_RESUME_PATH)
        self.prompt_template_path = os.path.expanduser(PROMPT_TEMPLATE_PATH)

        # Ensure test directories exist
        os.makedirs(os.path.dirname(self.baseline_resume_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.prompt_template_path), exist_ok=True)

        # Sample content for test files
        self.sample_resume = "# John Doe Resume\n\n## Experience\n- Software Engineer at Example Corp"
        self.sample_template = "# Template\n\n## Resume:\n$baseline_resume\n\n## Job Description:\n$job_description"

        # Create test files if they don't exist
        if not os.path.exists(self.baseline_resume_path):
            with open(self.baseline_resume_path, 'w', encoding='utf-8') as f:
                f.write(self.sample_resume)

        if not os.path.exists(self.prompt_template_path):
            with open(self.prompt_template_path, 'w', encoding='utf-8') as f:
                f.write(self.sample_template)

        # Initialize managers with real paths
        self.resume_manager = ResumeManager(self.baseline_resume_path)
        self.prompt_manager = PromptTemplateManager(self.prompt_template_path)

    def test_resume_manager_init(self):
        """Test ResumeManager initialization with real file"""
        self.assertIsNotNone(self.resume_manager)
        self.assertEqual(self.resume_manager.resume_path,
                         Path(self.baseline_resume_path))
        # Verify content was loaded
        self.assertIsNotNone(self.resume_manager._baseline_content)

    def test_resume_manager_get_content(self):
        """Test ResumeManager.get_baseline_content with real file"""
        content = self.resume_manager.get_baseline_content()
        self.assertIsNotNone(content)
        # Should contain content from the file, not the default message
        self.assertNotIn("No baseline resume found", content)
        self.assertNotIn("Error loading baseline resume", content)

    def test_prompt_manager_init(self):
        """Test PromptTemplateManager initialization with real file"""
        self.assertIsNotNone(self.prompt_manager)
        self.assertEqual(self.prompt_manager.template_path,
                         Path(self.prompt_template_path))
        # Verify content was loaded
        self.assertIsNotNone(self.prompt_manager._template_content)

    def test_variable_substitution(self):
        """Test variable substitution in the template"""
        variables = {
            "baseline_resume": "My test resume",
            "job_description": "Sample job description"
        }

        result = self.prompt_manager.substitute_variables(variables)
        self.assertIn("My test resume", result)
        self.assertIn("Sample job description", result)

    def test_reload_functions(self):
        """Test reload functions for both managers"""
        # First modify the files
        with open(self.baseline_resume_path, 'a', encoding='utf-8') as f:
            f.write("\n- Updated resume content")

        with open(self.prompt_template_path, 'a', encoding='utf-8') as f:
            f.write("\n\n## Updated template section")

        # Reload from files
        self.resume_manager.reload_baseline()
        self.prompt_manager.reload_template()

        # Check updated content was loaded
        self.assertIn("Updated resume content",
                      self.resume_manager.get_baseline_content())
        result = self.prompt_manager.substitute_variables(
            {"baseline_resume": "resume", "job_description": "job"})
        self.assertIn("Updated template section", result)


class TestResumeManagerWithMissingFiles(unittest.TestCase):
    """Test ResumeManager behavior with missing files"""

    def setUp(self):
        # Create a temporary file path that doesn't exist
        fd, path = tempfile.mkstemp()
        os.close(fd)
        os.unlink(path)  # Ensure the file doesn't exist
        self.nonexistent_file = path

    def test_missing_resume_file(self):
        """Test ResumeManager behavior when file is missing"""
        manager = ResumeManager(self.nonexistent_file)
        content = manager.get_baseline_content()
        self.assertIn("No baseline resume found", content)

    def test_reload_with_missing_file(self):
        """Test reload behavior with missing file"""
        manager = ResumeManager(self.nonexistent_file)
        # Initial state has the default message
        self.assertIn("No baseline resume found",
                      manager.get_baseline_content())

        # Now create the file
        with open(self.nonexistent_file, 'w', encoding='utf-8') as f:
            f.write("New resume content")

        # Reload and check content
        manager.reload_baseline()
        self.assertEqual("New resume content", manager.get_baseline_content())

        # Clean up
        os.unlink(self.nonexistent_file)


class TestPromptManagerWithMissingFiles(unittest.TestCase):
    """Test PromptTemplateManager behavior with missing files"""

    def setUp(self):
        # Create a temporary file path that doesn't exist
        fd, path = tempfile.mkstemp()
        os.close(fd)
        os.unlink(path)  # Ensure the file doesn't exist
        self.nonexistent_file = path

    def test_missing_template_file(self):
        """Test PromptTemplateManager behavior when file is missing"""
        manager = PromptTemplateManager(self.nonexistent_file)
        variables = {"baseline_resume": "resume", "job_description": "job"}
        content = manager.substitute_variables(variables)
        # Should use default template
        self.assertIn("CRITICAL CONSTRAINTS", content)
        self.assertIn("resume", content)
        self.assertIn("job", content)

    def test_reload_with_missing_file(self):
        """Test reload behavior with missing file"""
        manager = PromptTemplateManager(self.nonexistent_file)
        # Initial state has the default template

        # Now create the file
        with open(self.nonexistent_file, 'w', encoding='utf-8') as f:
            f.write("Custom template: $baseline_resume / $job_description")

        # Reload and check content
        manager.reload_template()
        result = manager.substitute_variables(
            {"baseline_resume": "resume", "job_description": "job"})
        self.assertEqual("Custom template: resume / job", result)

        # Clean up
        os.unlink(self.nonexistent_file)


class TestErrorCases(unittest.TestCase):
    """Test error handling in both managers"""

    @patch('builtins.open', side_effect=Exception("Test error"))
    def test_resume_manager_general_error(self, mock_open):
        """Test ResumeManager behavior with general errors"""
        manager = ResumeManager("some/path.md")
        content = manager.get_baseline_content()
        self.assertEqual("Error loading baseline resume.", content)

    @patch('builtins.open', side_effect=Exception("Test error"))
    def test_prompt_manager_general_error(self, mock_open):
        """Test PromptTemplateManager behavior with general errors"""
        manager = PromptTemplateManager("some/path.md")
        # Should use default template
        self.assertIn("CRITICAL CONSTRAINTS",
                      manager._template_content)  # type: ignore

    def test_invalid_template_variables(self):
        """Test error handling with invalid template variables"""
        # Create a template with syntax error
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            f.write("Template with $invalid syntax ${")
            temp_path = f.name

        # Create manager with problematic template
        manager = PromptTemplateManager(temp_path)

        # This should raise an exception
        with self.assertRaises(Exception):
            manager.substitute_variables(
                {"baseline_resume": "resume", "job_description": "job"})

        # Clean up
        os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
