#!/usr/bin/env python3
"""
Resume management for resume tailoring
"""

import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)


class ResumeManager:
    """Handles baseline resume loading and processing"""

    def __init__(self, resume_path: str):
        self.resume_path = Path(resume_path)
        self._baseline_content = None
        self._load_baseline()

    def _load_baseline(self):
        """Load baseline resume from file"""
        try:
            with open(self.resume_path, 'r', encoding='utf-8') as f:
                self._baseline_content = f.read()
            logger.info(f"Loaded baseline resume from {self.resume_path}")
        except FileNotFoundError:
            logger.error(f"Baseline resume file not found: {self.resume_path}")
            self._baseline_content = "No baseline resume found. Please provide your professional experience."
        except Exception as e:
            logger.error(f"Error loading baseline resume: {e}")
            self._baseline_content = "Error loading baseline resume."

    def get_baseline_content(self) -> str:
        """Get the baseline resume content"""
        return self._baseline_content or "No baseline resume available"

    def reload_baseline(self):
        """Reload baseline resume from file"""
        self._load_baseline()
