"""
Unit tests for Obsidian utility functions
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from resume_mcp.utils.obsidian import (
    save_obsidian_file,
    read_obsidian_file,
    fuzzy_search_files
)


class TestObsidianUtils:
    """Tests for Obsidian utility functions"""

    @patch("resume_mcp.utils.obsidian.open")
    @patch("resume_mcp.utils.obsidian.os.path.join")
    @patch("resume_mcp.utils.obsidian.OBSIDIAN_VAULT", "/mock/vault")
    def test_save_obsidian_file(self, mock_join, mock_open):
        """Test saving a file to the Obsidian vault"""
        # Setup mocks
        mock_join.return_value = "/mock/vault/test.md"
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        # Call function
        result = save_obsidian_file("Test content", "test.md")

        # Assertions
        mock_join.assert_called_with("/mock/vault", "test.md")
        mock_open.assert_called_with(
            "/mock/vault/test.md", mode="w", encoding='utf-8')
        mock_file.write.assert_called_with("Test content")
        assert result == "/mock/vault/test.md"

    @patch("resume_mcp.utils.obsidian.Path")
    @patch("resume_mcp.utils.obsidian.open")
    @patch("resume_mcp.utils.obsidian.OBSIDIAN_VAULT", "/mock/vault")
    def test_read_obsidian_file(self, mock_open, mock_path):
        """Test reading a file from the Obsidian vault"""
        # Setup mocks
        mock_path.return_value = MagicMock()
        mock_match = MagicMock()
        mock_path.return_value.rglob.return_value.__next__.return_value = mock_match
        mock_file = MagicMock()
        mock_file.read.return_value = "Test content"
        mock_open.return_value.__enter__.return_value = mock_file

        # Call function
        result = read_obsidian_file("test")

        # Assertions
        mock_path.assert_called_with("/mock/vault")
        mock_path.return_value.rglob.assert_called_with("test.md")
        mock_open.assert_called_with(mock_match, mode='r', encoding='utf-8')
        assert result == "Test content"

    @patch("resume_mcp.utils.obsidian.Path")
    @patch("resume_mcp.utils.obsidian.OBSIDIAN_VAULT", "/mock/vault")
    def test_fuzzy_search_files(self, mock_path):
        """Test fuzzy search for files in the Obsidian vault"""
        # Setup mock files
        mock_files = [
            MagicMock(stem="resume", suffix=".md",
                      **{"relative_to.return_value": "resume.md", "__str__": MagicMock(return_value="/mock/vault/resume.md")}),
            MagicMock(stem="resume-template", suffix=".md",
                      **{"relative_to.return_value": "resume-template.md", "__str__": MagicMock(return_value="/mock/vault/resume-template.md")}),
            MagicMock(stem="work-history", suffix=".md",
                      **{"relative_to.return_value": "work-history.md", "__str__": MagicMock(return_value="/mock/vault/work-history.md")}),
            MagicMock(stem="projects", suffix=".md",
                      **{"relative_to.return_value": "projects.md", "__str__": MagicMock(return_value="/mock/vault/projects.md")})
        ]
        mock_path.return_value = MagicMock()
        mock_path.return_value.rglob.return_value = mock_files

        # Call function
        results = fuzzy_search_files("resume", min_score=55)

        # Assertions
        mock_path.assert_called_with("/mock/vault")
        mock_path.return_value.rglob.assert_called_with("*.md")

        # Check that we got results back and they're sorted by score
        assert len(results) > 0

        # Test exact match comes first
        assert results[0]["filename"] == "resume"
        assert results[0]["score"] == 100

        # Test partial match appears in results
        resume_template_found = False
        for result in results:
            if result["filename"] == "resume-template":
                resume_template_found = True
                break
        assert resume_template_found

        # Test that scores are sorted in descending order
        for i in range(len(results) - 1):
            assert results[i]["score"] >= results[i+1]["score"]

    @patch("resume_mcp.utils.obsidian.Path")
    @patch("resume_mcp.utils.obsidian.OBSIDIAN_VAULT", "/mock/vault")
    def test_fuzzy_search_min_score(self, mock_path):
        """Test fuzzy search with custom minimum score"""
        # Setup mock files
        mock_files = [
            MagicMock(stem="resume", suffix=".md",
                      **{"relative_to.return_value": "resume.md", "__str__": MagicMock(return_value="/mock/vault/resume.md")}),
            MagicMock(stem="unrelated", suffix=".md",
                      **{"relative_to.return_value": "unrelated.md", "__str__": MagicMock(return_value="/mock/vault/unrelated.md")})
        ]
        mock_path.return_value = MagicMock()
        mock_path.return_value.rglob.return_value = mock_files

        # Call function with high min_score
        results = fuzzy_search_files("resume", min_score=90)

        # Should only match "resume" with high score
        assert len(results) == 1
        assert results[0]["filename"] == "resume"

    @patch("resume_mcp.utils.obsidian.Path")
    @patch("resume_mcp.utils.obsidian.OBSIDIAN_VAULT", "/mock/vault")
    def test_fuzzy_search_limit(self, mock_path):
        """Test fuzzy search with custom limit"""
        # Setup many mock files
        mock_files = [
            MagicMock(stem=f"resume-{i}", suffix=".md",
                      **{"relative_to.return_value": f"resume-{i}.md", "__str__": MagicMock(return_value=f"/mock/vault/resume-{i}.md")})
            for i in range(10)
        ]
        mock_path.return_value = MagicMock()
        mock_path.return_value.rglob.return_value = mock_files

        # Call function with custom limit
        results = fuzzy_search_files("resume", limit=3)

        # Should only return 3 results maximum
        assert len(results) == 3


if __name__ == "__main__":
    pytest.main(["-v", "test_obsidian.py"])
